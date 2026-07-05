---
name: union-root-dynamic-path-iteration
description: When testing iteration step functions with a union as the root node,
  verify that all nodes in the union are correctly marked as on the dynamic path.
  This skill catches bugs where BinaryUnionReplacer fails to preserve dynamic path
  properties when replacing binary unions with NAryUnionPlanNode inside iterations.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# union-root-dynamic-path-iteration

## Instructions

# Iteration Union Root Dynamic Path Verification

## Instructions

- WHEN the TG encounters an iteration (BulkIteration or DeltaIteration) whose step function (closeWith call) has a `union()` operation as the root node (i.e., the union outputs directly into the iteration's result)
- THEN the TG should write a test that:
  1. Creates an `IterativeDataSet` (for bulk) or `DeltaIteration` (for workset) with a union as the step function root
  2. Compiles the plan using `compileNoStats(p)` from `CompilerTestBase`
  3. Extracts the `BulkIterationPlanNode` or `WorksetIterationPlanNode` from the sink
  4. Retrieves the root NoOp node of the step function via `iterNode.getRootOfStepFunction()` (bulk) or `iterNode.getNextWorkSetPlanNode()`/`iterNode.getSolutionSetDeltaPlanNode()` (workset)
  5. Retrieves the `NAryUnionPlanNode` that is the source of that NoOp
  6. Asserts that the NoOp is on the dynamic path: `assertTrue(noop.isOnDynamicPath())` and has a cost weight >= 1: `assertTrue(noop.getCostWeight() >= 1)`
  7. Asserts that the union node is on the dynamic path: `assertTrue(union.isOnDynamicPath())` and has a cost weight >= 1: `assertTrue(union.getCostWeight() >= 1)`
  8. Calls `new JobGraphGenerator().compileJobGraph(op)` to verify the plan can be translated to a JobGraph without exceptions

- Common pitfalls to avoid:
  - Do NOT assume the union is the direct input of the iteration root — the optimizer inserts a NoOp between the union and the iteration's root of step function. The assertion chain must go: `iterNode.getRootOfStepFunction()` (returns NoOp) → `noop.getInput().getSource()` (returns union).
  - Do NOT test with a single input to the iteration — the bug specifically manifests when a `union()` is used as the root of the step function, causing the `BinaryUnionReplacer` to process it.
  - Do NOT forget to assert both `isOnDynamicPath()` AND `getCostWeight() >= 1` — the bug may cause the node to be on the dynamic path but with incorrect cost weight (0 instead of >= 1).
  - For workset iterations, test BOTH the next workset union AND the solution set delta union — both must be on the dynamic path.

- Example (correct):
```java
@Test
public void testIterationWithUnionRoot() {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(43);
    
    IterativeDataSet<Long> iteration = env.generateSequence(-4, 1000).iterate(100);
    
    iteration.closeWith(
            iteration.map(new IdentityMapper<Long>()).union(iteration.map(new IdentityMapper<Long>())))
            .output(new DiscardingOutputFormat<Long>());
    
    Plan p = env.createProgramPlan();
    OptimizedPlan op = compileNoStats(p);
    
    SinkPlanNode sink = op.getDataSinks().iterator().next();
    BulkIterationPlanNode iterNode = (BulkIterationPlanNode) sink.getInput().getSource();
    
    SingleInputPlanNode noop = (SingleInputPlanNode) iterNode.getRootOfStepFunction();
    NAryUnionPlanNode union = (NAryUnionPlanNode) noop.getInput().getSource();
    
    assertTrue(noop.isOnDynamicPath());
    assertTrue(noop.getCostWeight() >= 1);
    assertTrue(union.isOnDynamicPath());
    assertTrue(union.getCostWeight() >= 1);
    
    new JobGraphGenerator().compileJobGraph(op);
}
```

- Example (incorrect — missing dynamic path assertions):
```java
// WRONG: Only checks compilation, doesn't verify dynamic path
@Test
public void testIterationWithUnionRoot() {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
    IterativeDataSet<Long> iteration = env.generateSequence(-4, 1000).iterate(100);
    iteration.closeWith(
            iteration.map(new IdentityMapper<Long>()).union(iteration.map(new IdentityMapper<Long>())))
            .output(new DiscardingOutputFormat<Long>());
    
    Plan p = env.createProgramPlan();
    OptimizedPlan op = compileNoStats(p);
    new JobGraphGenerator().compileJobGraph(op); // May pass even if dynamic path is wrong!
}
```