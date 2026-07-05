---
name: property-index-path-based-cost-estimation
description: When testing PropertyIndex cost estimation with path-based queries, the
  TG should verify that the cost returned for a path-restricted query (using Filter.PropertyRestriction
  with a path) matches an expected value. The bug causes incorrect cost (12.0 instead
  of 6.0) for indexed properties queried with a path restriction.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# property-index-path-based-cost-estimation

## Instructions

# PropertyIndex Path-Based Cost Estimation

## Instructions

**WHEN** the TG encounters code in `PropertyIndex` or `PropertyIndexPlan` that estimates the cost of a property index lookup, and the cost depends on whether a `Filter` has a path restriction (i.e., `Filter.PropertyRestriction` with a path),

**THEN** the TG should write a test that:
1. Creates a `NodeState` tree with at least two distinct subtrees, each containing the same indexed property with values.
2. Registers a `PropertyIndex` on the property (e.g., "myProp").
3. Constructs a `Filter` with a path restriction that narrows the query to only one of the subtrees (e.g., path = "/subtree1").
4. Calls `PropertyIndex.getCost(...)` (or `PropertyIndexPlan.getCost(...)`) with that `Filter`.
5. Asserts that the returned cost equals the **expected cost for only that subtree**, not the cost of the entire index.
6. On the buggy version, the cost returned is **12.0** (cost of the whole index). On the fixed version, the cost should be **6.0** (cost of only the filtered subtree).

**Common pitfalls to avoid:**
- Testing cost estimation **without** a path restriction — the bug only manifests when a path restriction is applied.
- Testing cost estimation with an empty tree or single-subtree tree — the bug requires multiple subtrees to expose incorrect cost aggregation.
- Testing only the `count()` method directly instead of the cost estimation pipeline (`PropertyIndex.getCost()` → `PropertyIndexPlan.getCost()`).

**Example (correct):**
```java
// Arrange: create a root with two subtrees, each with indexed property
NodeState root = ... // root with /a and /b subtrees
// /a and /b each contain a node with property "myProp" = "value1"
PropertyIndex index = new PropertyIndex("myProp");
Filter filter = ... // Filter with path restriction = "/a"

// Act
double cost = index.getCost(root, null, filter, Collections.singleton("value1"));

// Assert
assertEquals("Expected path-restricted cost", 6.0, cost, 0.001);
```

**Example (incorrect — will not catch the bug):**
```java
// ❌ Wrong: no path restriction, so cost is always correct
double cost = index.getCost(root, null, filter, Collections.singleton("value1"));
assertEquals(12.0, cost, 0.001); // This passes on both buggy and fixed — useless test!
```