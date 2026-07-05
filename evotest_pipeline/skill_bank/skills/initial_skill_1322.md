---
name: union-node-multiple-outputs
description: When a union node's output is consumed by more than one successor, the
  compiler may compute conflicting execution plans for the same union. This skill
  teaches how to write tests that verify correct plan compilation when a union feeds
  multiple operators.
code_tags:
- UNION_MULTIPLE_OUTPUTS
test_pattern: PARAMETRIC_TEST
---

# union-node-multiple-outputs

## Instructions

# Union Node with Multiple Outputs

## Instructions

- WHEN the TG encounters a `BinaryUnionNode` or `NAryUnionPlanNode` whose output feeds **more than one consumer** (e.g., a union is the source of two different `GroupReduceFunction` operators)
- THEN the TG should write a test that:
  1. Constructs a dataflow where a union feeds at least two downstream operators (e.g., two `GroupReduce` transformations)
  2. Calls `Optimizer.getCompiler().compile(plan)` to compile the plan
  3. Verifies that **no exception is thrown** during compilation
  4. Verifies the resulting `OptimizedPlan` is not null
  5. Verifies that the `NAryUnionPlanNode` in the optimized plan has exactly the expected number of inputs (e.g., 3 inputs when uniting 3 sources)
- The test should specifically catch the case where the compiler tries to assign conflicting execution strategies to the same union node due to different requirements from its multiple consumers
- Common pitfalls:
  - Testing the union with only a single consumer (the happy path passes even on the buggy version)
  - Only testing that the union is present without verifying the plan compiles successfully
  - Assuming that union nodes behave identically whether they have one or multiple outputs

### Correct Example (Union feeding two consumers):

```java
// Correct: Tests compilation of a union that feeds two downstream operators
@Test
public void testUnionReplacement() throws Exception {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
    DataSet<Long> input1 = env.generateSequence(1, 3);
    DataSet<Long> input2 = env.generateSequence(4, 6);
    DataSet<Long> input3 = env.generateSequence(7, 9);

    DataSet<Long> union = input1.union(input2).union(input3);

    // Two consumers on the same union
    DataSet<Long> groupRed1 = union.groupBy(new IdentitySelector()).reduceGroup(new IdentityReducer());
    DataSet<Long> groupRed2 = union.groupBy(new IdentitySelector()).reduceGroup(new IdentityReducer());

    DataSet<Long> result = groupRed1.union(groupRed2);
    result.output(new DiscardingOutputFormat<Long>());

    Plan plan = env.createProgramPlan();
    OptimizedPlan oPlan = Optimizer.getCompiler().compile(plan);

    assertNotNull(oPlan);

    // Verify the NAryUnionPlanNode exists with 3 inputs
    boolean found = false;
    for (PlanNode node : oPlan.getAllNodes()) {
        if (node instanceof NAryUnionPlanNode) {
            assertEquals(3, ((NAryUnionPlanNode) node).getListOfInputs().size());
            found = true;
        }
    }
    assertTrue("No NAryUnionPlanNode found in optimized plan", found);
}
```

### Incorrect Example (Single consumer — misses the bug):

```java
// Incorrect: Only one consumer on the union — compiles even on buggy version
@Test
public void testUnionReplacement() throws Exception {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
    DataSet<Long> input1 = env.generateSequence(1, 3);
    DataSet<Long> input2 = env.generateSequence(4, 6);
    DataSet<Long> input3 = env.generateSequence(7, 9);

    DataSet<Long> union = input1.union(input2).union(input3);

    // Only one consumer — does NOT trigger the bug
    DataSet<Long> groupRed = union.groupBy(new IdentitySelector()).reduceGroup(new IdentityReducer());
    groupRed.output(new DiscardingOutputFormat<Long>());

    Plan plan = env.createProgramPlan();
    OptimizedPlan oPlan = Optimizer.getCompiler().compile(plan);
    // This passes even on the buggy version
}
```