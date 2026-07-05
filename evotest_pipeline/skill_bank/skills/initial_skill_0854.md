---
name: aggregate-reaggregation-mixin-resolution
description: When testing aggregate index configurations that involve mixin types,
  ensure that reaggregation logic resolves mixin node types during template merge,
  not just primary types. Without this, mixin-aggregated nodes are lost during re-aggregation.
code_tags:
- AGGREGATE_NODE_TYPE_RESOLUTION
- AGGREGATE_MERGE
- AGGREGATE_REAGGERATION
test_pattern: STATE_TEST
---

# aggregate-reaggregation-mixin-resolution

## Instructions

# Aggregate Reaggregation with Mixin Node Types

## Instructions

- WHEN the TG encounters aggregate index configurations where node types are resolved via `ConfigUtil.getPrimaryTypeName(nodeState)` and `ConfigUtil.getMixinNames(nodeState)` — specifically in the `Aggregate` class's `getIncludedIndexedNode` or `collectIndexedNode` methods — AND there is a reaggregation/merge step that combines multiple aggregate templates (e.g., from primary type AND mixin types into a single merged template)
- THEN the TG should write a STATE_TEST that:
  1. Creates a test node tree where a node of a certain primary type ALSO has a mixin type that defines its own aggregate node includes (e.g., node of type `app:Page` with mixin `app:PageMixin`, where `app:Page` aggregates child nodes `jcr:content` and `app:PageMixin` aggregates a different child like `coverImage`)
  2. Calls the aggregation logic that triggers a reaggregation (e.g., `agg.getIncludedIndexedNode(rootNodeState)` which internally calls `AggregateRoot.getNodeState()` and triggers `NodeState.getChildNode("myNode")` to force lazy loading and trigger the `collectIndexedNode` path)
  3. Verifies that the resulting `AggregateRoot` (or list of indexed nodes) contains entries from BOTH the primary type AND the mixin type aggregates — specifically that the count of aggregate node includes equals the sum of includes from the primary type template AND all matching mixin type templates
  4. For the buggy version, expects a lower count (e.g., `expected:<4> but was:<0>`) because the reaggregation step fails to collect nodes defined by mixin aggregates
- Common pitfalls:
  - Testing with only a single node type (no mixin involved) — this skill is specifically about the interaction between primary type and mixin type aggregates during merge/reaggregation
  - Assuming that simply creating an `Aggregate` from index definition and calling methods directly is sufficient — the bug manifests when a node is loaded lazily from the tree (via `NodeState.getChildNode`) which triggers the full `collectIndexedNode` path, not the direct `getIncludedIndexedNode` path
  - Forgetting to set up the index definition (oak:queryIndexDefinition) with proper `aggregates` and `reaggregate` configuration that includes both primary type and mixin type aggregates
  - Only checking the primary type aggregate includes without verifying that mixin-type aggregate includes are also present after merge

## Correct Example (what a good test looks like)

```java
// In AggregateTest.java
@Test
public void testReaggregateMixin() throws Exception{
    // Setup: create index definition with aggregates for app:Page AND app:PageMixin
    NodeState indexDef = createIndexDef(
        createAggregates(
            // Primary type aggregate
            "app:Page", asList(
                createAggInclude("jcr:content"),
                createAggInclude("coverImage")
            ),
            // Mixin type aggregate
            "app:PageMixin", asList(
                createAggInclude("coverImage"),
                createAggInclude("app:footer")
            )
        )
    );

    // Setup: create type provider with both node types
    TypeProvider typeProvider = new TypeProvider(/*...*/);

    // Setup: create root node with a child having primary type + mixin
    NodeState root = createNodeState(
        createNode("mytest",
            createProperty("jcr:primaryType", "app:Page"),
            createProperty("jcr:mixinTypes", "app:PageMixin"),
            createNode("jcr:content", createProperty("foo", "bar")),
            createNode("coverImage", createProperty("img", "test")),
            createNode("app:footer", createProperty("link", "test"))
        )
    );

    Aggregate aggregate = new Aggregate(indexDef, typeProvider);

    // Trigger: set up the aggregate to find node via primary type match,
    // which triggers getIncludedIndexedNode -> reaggregation
    // This is done by creating the AggregateNode for 'mytest', then forcing
    // lazy loading of the node to trigger the collectIndexedNode code path
    // that uses NodeState.getChildNode()
    NodeState myNode = root.getChildNode("mytest");
    AggregatedNode aggregated = aggregate.getIncludedIndexedNode(myNode);
    
    // Verify: all 4 aggregate includes are present (2 from primary + 2 from mixin)
    assertEquals(4, aggregated.getNodeStates().size());

    // Further verify specific includes are present
    // ...
}
```

## Incorrect Example (what the TG might write)

```java
// BAD: Only tests primary type aggregate, doesn't trigger reaggregation path
@Test
public void testReaggregateMixin_bad(){
    // Only sets up one aggregate for the primary type
    NodeState indexDef = createIndexDef(
        createAggregates(
            "app:Page", asList(
                createAggInclude("jcr:content"),
                createAggInclude("coverImage")
            )
        )
    );
    
    TypeProvider typeProvider = new TypeProvider(/*...*/);
    
    NodeState root = createNodeState(
        createNode("mytest",
            createProperty("jcr:primaryType", "app:Page"),
            createProperty("jcr:mixinTypes", "app:PageMixin"), // mixin type defined but no corresponding aggregate in index def
            createNode("jcr:content", createProperty("foo", "bar")),
            createNode("coverImage", createProperty("img", "test"))
        )
    );
    
    assertEquals(2, aggregate.getIncludedIndexedNode(root.getChildNode("mytest")).getNodeStates().size());
    // Expected: 4, but only tests 2 because mixin aggregates are missing from index def
}
```