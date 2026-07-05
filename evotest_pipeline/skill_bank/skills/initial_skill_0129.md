---
name: iteration-union-root-null-pointer
description: When compiling bulk iterations with a NAryUnionPlanNode as the root of
  the partial solution (e.g., a Union operator at the iteration body's output), the
  NepheleJobGraphGenerator may encounter a null node reference when traversing the
  union's predecessors. This skill teaches how to write a test that exercises this
  specific compiler path to catch such null-pointer errors.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# iteration-union-root-null-pointer

## Instructions

# Iteration Union Root Null Pointer

## Instructions

- WHEN the TG encounters code that traverses a `PlanNode` tree (such as `NepheleJobGraphGenerator` visiting `PlanNode` instances) and the traversal logic checks `node instanceof SourcePlanNode` or `node instanceof NAryUnionPlanNode` before examining predecessor/successor relationships,
- THEN the TG should write a test that carefully constructs a dataflow plan where a `NAryUnionPlanNode` is used as the **root** or **partial solution** node of a `BulkIterationPlanNode`. Specifically:
  1. Create a `BulkIterationPlanNode` whose partial solution (the output of the iteration body) is a `NAryUnionPlanNode` instead of a concrete operator node.
  2. Ensure the `NAryUnionPlanNode` has at least one predecessor (input).
  3. Then invoke `NepheleJobGraphGenerator` on the iteration plan (e.g., calling `jgg.translateToJobGraph(plan)` or similar plan-compilation entry point).
  4. Verify that the compilation succeeds without throwing a `NullPointerException` or an error containing the string `"Error translating node"`.
- The test should verify that the traversal does not assume a non-null return from visiting a `NAryUnionPlanNode`'s predecessors via a method that may return `null` instead of a valid `JobVertex` — the bug is that the visitor did not handle the case where visiting a `NAryUnionPlanNode` (especially when it is the iteration's `rootOfPartialSolution`) returned `null`, which then caused a `NullPointerException` when trying to dereference methods like `getParallelism()` or `getSinks()` on the `null` result.

**Common pitfalls to avoid:**
- Testing only iteration bodies that end with a `MapOperator` or `ReduceOperator` (concrete operators) — the union root case is what triggers the bug.
- Assuming the iteration plan node always has a valid predecessor that returns a non-null `JobVertex` — the `NAryUnionPlanNode` visitor may return `null` and this needs to be handled.
- Forgetting to check that the `NAryUnionPlanNode` is the **root of the partial solution** specifically; having a union elsewhere in the plan may not trigger the bug.

**Example of correct test structure:**
```java
// Pseudocode: Construct a bulk iteration where the partial solution
// ends with a Union (NAryUnionPlanNode)
BulkIterationPlanNode iterationPlanNode = ...;
// Ensure the rootOfPartialSolution is a NAryUnionPlanNode
assertTrue(iterationPlanNode.getRootOfPartialSolution() instanceof NAryUnionPlanNode);

try {
    NepheleJobGraphGenerator jgg = new NepheleJobGraphGenerator();
    JobGraph jobGraph = jgg.translateToJobGraph(plan);
    // Success: no NullPointerException
} catch (Exception e) {
    fail("Should not throw exception, but got: " + e.getMessage());
}
```

**Example of what would miss the bug:**
```java
// WRONG: This does not test the NAryUnionPlanNode root case
BulkIterationPlanNode iterationPlanNode = ...;
// The root is a MapOperator or some concrete operator
assertTrue(iterationPlanNode.getRootOfPartialSolution() instanceof MapOperator);
// This test passes even with the bug, because the union root path is never exercised
NepheleJobGraphGenerator jgg = new NepheleJobGraphGenerator();
JobGraph jobGraph = jgg.translateToJobGraph(plan); // no error, but not testing the bug
```