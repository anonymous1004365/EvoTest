---
name: ordered-index-multivalue-rejection
description: When an ordered Lucene index definition has a property with multiple
  values, the indexer must not throw an exception. Use this skill to test that ordered
  properties reject multi-valued content gracefully.
code_tags:
- VALIDATION
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# ordered-index-multivalue-rejection

## Instructions

# Ordered Index Multi-Value Rejection

## Instructions

- WHEN the TG encounters an Ordered Lucene index definition (an index with an `ordered` property set to `true`) AND a property that stores multiple values (e.g., a `String` property with `["val1", "val2"]`)
- THEN the TG should write a test that:
  1. Creates an index definition with the `ordered` flag enabled (e.g., via `NodeStateBuilder` or `IndexDefinitionBuilder` with `.ordered()` or `.property("propName").ordered(true)`)
  2. Adds a node that has a **multi-valued property** (e.g., `jcr:title` with values `["foo", "bar"]`) that the ordered index definition targets
  3. Adds that node to the workspace using `root.getTree("/")` and `tree.addChild(...)`
  4. Calls `root.commit()` or equivalent
  5. Expects **no exception** to be thrown (i.e., the test must pass without an `Exception` from the indexing pipeline)
- The test should verify that the commit succeeds even though the ordered property has multiple values.
- **Common pitfalls**:
  - Testing only with single-valued properties — the bug only manifests when the ordered property has **multiple values** (an array/list of values)
  - Forgetting to enable the `ordered` flag on the property definition in the index
  - Forgetting to register the index definition before the commit (e.g., via `NodeBuilder` manipulation of `/oak:index`)
  - Using an unordered index definition — the bug is specific to `ordered=true` indices

### Example (for reference — TG should adapt to the project's test framework)

**Correct test approach** (conceptual):
```java
// Build an ordered index definition
IndexDefinitionBuilder idxBuilder = new IndexDefinitionBuilder();
idxBuilder.indexRule("nt:base").property("myProp").ordered(true);
NodeBuilder indexBuilder = root.getTree("/oak:index/myIndex").getNodeBuilder();
NodeState index = idxBuilder.build();
// ... set index definition into the tree ...

// Add a node with multi-valued property
Tree content = root.getTree("/").addChild("testNode");
content.setProperty("myProp", Arrays.asList("val1", "val2"));

// Commit — this must NOT throw
root.commit();
```

**Incorrect test approach** (does not trigger the bug):
```java
// Only single value — bug not triggered
Tree content = root.getTree("/").addChild("testNode");
content.setProperty("myProp", "singleValue");
root.commit(); // passes even on buggy version
```

```java
// Forgetting ordered=true — bug not triggered
IndexDefinitionBuilder idxBuilder = new IndexDefinitionBuilder();
idxBuilder.indexRule("nt:base").property("myProp"); // no ordered() call
// ...
root.commit(); // passes even on buggy version
```