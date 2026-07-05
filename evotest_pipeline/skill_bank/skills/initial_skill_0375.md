---
name: property-index-cost-estimation-overflow
description: When testing cost estimation logic for query indexes, the TG should verify
  that estimated costs don't exceed traversal cost due to floating-point arithmetic
  overflow. This skill covers testing for double-precision overflow in cost ratio
  calculations like count * 1.0 / total * traversalCost.
code_tags:
- OVERFLOW
- BOUNDARY_CHECK
- FLOAT_PRECISION_ESTIMATION
test_pattern: PERFORMANCE_TEST
---

# property-index-cost-estimation-overflow

## Instructions

# Property Index Cost Estimation Overflow Test

## Instructions

- WHEN the TG encounters cost estimation/projection logic that computes a ratio like `entryCount * 1.0 / totalEntries * traversalCost` to estimate query cost for an index
- THEN it should verify that the estimated cost does NOT exceed the traversal cost (i.e., `estimatedCost <= traversalCost`) when the number of matching entries equals the index size
  - The expected behavior is that when `entryCount == totalEntries`, the ratio is 1.0 and the cost should equal `traversalCost` exactly
  - Due to double-precision floating-point overflow, `entryCount * 1.0 / totalEntries` with very large numbers (e.g., totalEntries = 6.7108864E7) can produce a value > 1.0 (e.g., 1.0000001), inflating the estimated cost above `traversalCost`
  - The test should use `assertTrue("Estimated cost for " + totalEntries + " nodes should not be higher than traversal (" + traversalCost + ")", estimatedCost <= traversalCost);`
- WHEN constructing the test data, the TG should:
  - Create a valid index definition (e.g., `PropertyIndex` with a `PropertyIndexPlan` and `PropertyIndexLookup`)
  - Register enough nodes so that `totalEntries` is a large number where `(totalEntries * 1.0 / totalEntries)` could overflow due to precision (e.g., 100 or 101 nodes with a traversal cost like 6.7108864E7)
  - Ensure the lookup finds all registered nodes, triggering the `entryCount == totalEntries` condition
- Common pitfalls to avoid:
  - Do NOT test only with small numbers (e.g., < 100 entries) where double precision is sufficient — the bug only manifests at scale
  - Do NOT forget to account for the scenario where ALL indexed entries match the query (entryCount == totalEntries)
  - Do NOT assume that `(n * 1.0 / n)` is always exactly 1.0 in double-precision arithmetic — it can be slightly > 1.0 for large n
  - Do NOT use integer arithmetic (e.g., `entryCount / totalEntries * traversalCost`) — this will always be 0 or incorrect
  - Do NOT only test with `eq` queries — also consider that the cost estimate may use `getEstimatedCost()` on a `PropertyIndexPlan` after executing a query that returns many results

- Example of correct test setup:
```java
// Setup: add many nodes under root
for (int i = 0; i < 101; i++) {
    // add nodes with property "foo"="bar"+i so PropertyIndex finds them
    root.getTree("/").addChild("node-" + i).setProperty("foo", "bar" + i);
}
root.commit();

// Create a PropertyIndexLookup and query for all matching entries
PropertyIndexLookup lookup = new PropertyIndexLookup(root);
long planEstimatedCost = ... // e.g. lookup.getCost(...) or plan.getEstimatedCost()
long traversalCost = ...; // e.g. 6.7108864E7
assertTrue("Estimated cost for 101 nodes should not be higher than traversal (" 
    + traversalCost + ")", planEstimatedCost <= traversalCost);
```

- Example of INCORRECT test (buggy — would pass on buggy code):
```java
// Only testing with small numbers
for (int i = 0; i < 3; i++) { ... }
// This wouldn't trigger the overflow bug
```