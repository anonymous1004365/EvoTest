---
name: lucene-index-cost-fulltext-vs-nodetype
description: When testing Lucene index planners that evaluate both fulltext and nodetype
  indexes, verify that fulltext indexes are correctly prioritized over nodetype-only
  indexes when both match. Test by creating indexes of both types on the same property
  and asserting the fulltext index is selected for fulltext queries.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# lucene-index-cost-fulltext-vs-nodetype

## Instructions

# Lucene Index Cost Calculation: Fulltext vs NodeType

## Instructions

### WHEN...
When the code implements logic for selecting between multiple Lucene indexes (e.g., a fulltext index and a node type index) that both match a property-based query plan, and the selection depends on cost comparison or index type preference.

### THEN...
Write a test that:
1. Creates a **fulltext property index** (e.g., via `IndexDefinitionBuilder` with `.fulltextEnabled(true)`) on a property such as `"jcr:title"` or similar.
2. Creates a **node type index** (e.g., via `IndexDefinitionBuilder` with `.fulltextEnabled(false)`) that also declares interest in the same property via `declaringNodeTypes` — use a node type like `"nt:base"` or a custom one.
3. Constructs a query plan that involves a **fulltext condition** on the same property (e.g., `NativeQuery` or `FullTextQuery` that references that property).
4. Calls the index planner's plan method (e.g., `IndexPlanner.plan()`) to obtain the plan result.
5. **Asserts that the fulltext index is selected**, not the node type-only index. For example, check that `planResult.getPlan().getPlanName()` or the cost/type indicates the fulltext index was chosen.

### What the test should verify:
- That the planner does not incorrectly prefer a node type index over a fulltext index when a fulltext query is issued.
- That cost comparisons between fulltext-enabled and non-fulltext indexes correctly account for the query type (fulltext vs. property-only).

### Common pitfalls to avoid:
- ❌ Testing only with a single index type (only fulltext or only nodetype) — this misses the selection logic.
- ❌ Using only property constraints without a fulltext condition — the bug is specific to fulltext queries.
- ❌ Assuming the index with lower cost is always selected — the planner may have hardcoded preferences for fulltext indexes regardless of cost.
- ❌ Not configuring `declaringNodeTypes` on the node type index — the node type index will not match without it.

### Example (Correct):

```java
// Given: a fulltext index on "jcr:title" and a nodetype index also on "jcr:title" via nt:base
IndexDefinition fulltextIdx = new IndexDefinitionBuilder()
    .noPropertyTree()
    .fulltextEnabled(true)
    .indexRule("nt:base")
        .property("jcr:title").propertyIndex()
    .build();

IndexDefinition nodetypeIdx = new IndexDefinitionBuilder()
    .noPropertyTree()
    .fulltextEnabled(false)
    .declaringNodeTypes("nt:base")
    .indexRule("nt:base")
        .property("jcr:title").propertyIndex()
    .build();

// When: planning a fulltext query on that property
IndexPlanner planner = new IndexPlanner(...);
PlanResult result = planner.plan();

// Then: the fulltext index should be preferred
assertTrue("Fulltext index should be selected over nodetype index",
    result.getPlan().getPlanName().contains("fulltext"));
```

### Example (Incorrect — Too Narrow):

```java
// ❌ Only tests one index
IndexDefinition fulltextIdx = new IndexDefinitionBuilder()
    .fulltextEnabled(true)
    .build();
IndexPlanner planner = new IndexPlanner(...);
PlanResult result = planner.plan();
assertNotNull(result.getPlan());
// Does not test the critical selection logic between competing indexes
```