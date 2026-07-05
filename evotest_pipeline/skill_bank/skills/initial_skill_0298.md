---
name: co-group-custom-partitioning-hash-conflict
description: When testing CoGroup operators with incompatible hash partitioning (groupBy)
  and custom partitioning (withPartitioner), verify that the optimizer detects and
  rejects the conflicting partitioning schemes by throwing a CompilerException.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# co-group-custom-partitioning-hash-conflict

## Instructions

# CoGroup Custom Partitioning Hash Conflict Test

## Instructions

WHEN the TG encounters a test for `CoGroup` (or `Join`) operators in the Flink optimizer that combines `.withPartitioner(new CustomPartitioner())` with `.groupBy(...)` (hash partitioning) on the same input:

- THEN it should construct a test that uses both a custom partitioner (set via `withPartitioner()`) AND a hash-based grouping (set via `groupBy(...)`) on the same DataSet within a CoGroup transformation.
- The test should invoke `TestBaseUtils.optimizePlan(plan)` to trigger the optimizer.
- The test should verify that the optimizer throws a `CompilerException` with a message containing "Too restrictive plan hints" to indicate that the conflicting partitioning schemes were detected.
- Use `Assert.assertNotNull(plan)` and expect the exception via `@Test(expected = CompilerException.class)`.
- Use `OperatorTestUtils.createProgramPlan()` or construct the plan manually with `ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment()`, adding two sources, applying a CoGroup with both `withPartitioner` and `groupBy`, and calling `env.createProgramPlan()`.

Common pitfalls:
- Testing only one input's partitioning while ignoring the other input's conflicting partitioning — both inputs in a CoGroup can independently set `withPartitioner` and `groupBy`, leading to conflicts on either side.
- Using `Join` tests to approximate `CoGroup` tests — the partitioning semantics differ; CoGroup uses separate key definitions for each input that can independently conflict with custom partitioners.
- Forgetting to set `@Test(expected = CompilerException.class)` on the test method.

Example of correct test code:
```java
@Test(expected = CompilerException.class)
public void testIncompatibleHashAndCustomPartitioning() {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

    DataSet<Tuple2<Long, Long>> input1 = env.fromElements(new Tuple2<>(0L, 0L));
    DataSet<Tuple2<Long, Long>> input2 = env.fromElements(new Tuple2<>(0L, 0L));

    input1.coGroup(input2)
        .where(new KeySelector<Tuple2<Long, Long>, Long>() {
            @Override
            public Long getKey(Tuple2<Long, Long> value) { return value.f0; }
        })
        .equalTo(new KeySelector<Tuple2<Long, Long>, Long>() {
            @Override
            public Long getKey(Tuple2<Long, Long> value) { return value.f0; }
        })
        .withPartitioner(new TestDistribution())
        .with(new DummyCoGroupFunction())
        .groupBy(0)
        .with(new DummyCoGroupFunction())
        .output(new DummyOutputFormat());

    Plan plan = env.createProgramPlan();
    TestBaseUtils.optimizePlan(plan);
}
```

Example of incorrect test code (missing the assertion/exception expectation):
```java
@Test
public void testIncompatibleHashAndCustomPartitioning() {
    // ... same setup ...
    Plan plan = env.createProgramPlan();
    // Missing: @Test(expected = CompilerException.class) or try-catch with fail()
    TestBaseUtils.optimizePlan(plan);  // This will throw but test won't catch it
}
```