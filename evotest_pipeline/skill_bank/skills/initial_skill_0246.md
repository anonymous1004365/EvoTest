---
name: sort-only-by-score-invalid-plan
description: When validating index plan generation with only sort-by-JCR_SCORE and
  no query filters, test that IndexPlanner returns an empty list (no plan) rather
  than attempting to create an invalid plan. This skill catches NullPointerException
  from missing plan data when sortOrder contains only jcr:score.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# sort-only-by-score-invalid-plan

## Instructions

# Sort-Only-by-Score Index Plan Validation

## Instructions

WHEN the Test Generator encounters a method that computes or returns an **IndexPlan** based on a **Filter** (e.g., `FilterImpl`) and a **List<OrderEntry>** containing only `JCR_SCORE` (i.e., `jcr:score`) with **no query constraints** — meaning the `Filter` has an empty or null property restriction set — THEN it should:

1. **Create a sort order** containing exactly one `OrderEntry` with `JCR_SCORE` (the constant `org.apache.jackrabbit.JcrConstants.JCR_SCORE`, value `"jcr:score"`) and direction `OrderEntry.Direction.DESCENDING`.
2. **Create a Filter** with **no property restrictions** (e.g., a `FilterImpl` with an empty property restrictions map).
3. **Call the plan-generation method** (e.g., `IndexPlanner.getPlans(filter, sortOrder, rootState)`) with these inputs.
4. **Assert that the returned list is empty** — i.e., `assertTrue(plans.isEmpty())` — because an index cannot produce a meaningful plan when only sorting by score with no query filtering.
5. **Avoid asserting against a single plan** or calling `.get(0)` on the result, as doing so will cause a `NullPointerException` or `IndexOutOfBoundsException` on the buggy version.

**Common pitfalls to avoid:**
- ❌ Testing only with non-empty property restrictions or with sort orders that include other properties (e.g., `jcr:lastModified`, `rep:score`) — this misses the specific edge case where score-only sorting triggers the bug.
- ❌ Calling `.get(0)` or any method on the first element of the returned plans list without first checking `isEmpty()`, as the buggy version may return an empty list and the test should validate that, not assume a plan exists.
- ❌ Using a null `sortOrder` or null `filter` — the bug is about an *empty result* with a non-null but score-only sort order, not about null inputs.
- ❌ Forgetting to import `JCR_SCORE` from `org.apache.jackrabbit.JcrConstants`.

**Correct test example:**
```java
@Test
public void noPlanForSortOnlyByScore() throws Exception {
    NodeState root = /* obtain root node state */;
    IndexPlanner planner = new IndexPlanner(/* setup */);
    
    // Sort order contains only jcr:score descending
    List<OrderEntry> sortOrder = Collections.singletonList(
        new OrderEntry(JCR_SCORE, OrderEntry.Direction.DESCENDING, OrderEntry.PropertyType.SCORE));
    
    // Filter with no property restrictions
    Filter filter = new FilterImpl(/* no restrictions */);
    
    List<IndexPlan> plans = planner.getPlans(filter, sortOrder, root);
    assertTrue("Expected no plans when sorting only by score", plans.isEmpty());
}
```

**Incorrect test example (would miss the bug):**
```java
@Test
public void missingEdgeCaseTest() throws Exception {
    // WRONG: Uses a filter with property restrictions — this does not trigger the bug
    Filter filter = someFilterWithRestrictions();
    List<OrderEntry> sortOrder = Collections.singletonList(
        new OrderEntry(JCR_SCORE, OrderEntry.Direction.DESCENDING, OrderEntry.PropertyType.SCORE));
    
    List<IndexPlan> plans = planner.getPlans(filter, sortOrder, root);
    // The buggy version might return a plan here (because restrictions exist),
    // so this test would not detect the empty-list-with-score-only bug
    assertFalse(plans.isEmpty());
}
```

## Why This Matters
Without this test, the `IndexPlanner.getPlans()` method can return an empty list when the sort order is score-only with no query filters, causing downstream code that expects a non-empty plan list to throw a `NullPointerException` or `IndexOutOfBoundsException`. The fix ensures the planner correctly returns no index plan in this scenario.