---
name: partitioning-pushdown-in-groupreduce
description: When testing optimizer planning for GroupReduceOperator with combiners,
  verify that partitioning strategies (PARTITION_HASH) are correctly preserved and
  not overridden to FORWARD. This skill applies to testing how the optimizer propagates
  partition requirements from interesting properties through driver strategies like
  GroupReduceWithCombineProperties and GroupCombineProperties.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# partitioning-pushdown-in-groupreduce

## Instructions

# Partitioning Pushdown in GroupReduce Optimizer Planning

## Instructions

- WHEN the TG encounters a test scenario involving `GroupReduceOperator` with a `GroupReduceFunction` and `CombineHint.HASH`, `Grouping` on a field, and the optimizer planning phase
- THEN the TG should verify that the **ship strategy** on the input `Channel` to the `GroupReduce` plan node is `ShipStrategyType.PARTITION_HASH` (not `FORWARD`), by calling `getInput().getShipStrategy()` on the plan node
- Specifically, build a data flow of the form: `Source → MapOperator → GroupBy(0).reduceGroup(…).withCombineHint(CombineHint.HASH)` and compile the plan to obtain `JobGraph`. Then check that the `GroupReduce` node's input shipping strategy remains `PARTITION_HASH`
- Include the concrete import: `org.apache.flink.runtime.operators.shipping.ShipStrategyType`
- Use `assertNotEquals(ShipStrategyType.FORWARD, …)` as a quick sanity check, and `assertEquals(ShipStrategyType.PARTITION_HASH, …)` as the positive assertion
- **Common pitfalls to avoid**:
  - Testing only with combiners disabled (no `CombineHint.OPTIMIZER_CHOOSES`) — enable `HASH` explicitly to trigger the bug
  - Assuming FORWARD is always wrong — the bug is that the optimizer incorrectly falls back to FORWARD when it should preserve the hash partition requirement
  - Forgetting to use a `MapOperator` before the `GroupReduce` — the bug manifests when an operator between source and reduce has conflicting interesting properties

## Example: Correct test (based on PartitionPushdownTest)

```java
@Test
public void testPartitioningNotPushedDown() {
    ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
    
    DataSet<Tuple2<Long, Long>> input = env.fromElements(new Tuple2<>(0L, 0L));
    
    input
        .map(new MapFunction<Tuple2<Long, Long>, Tuple2<Long, Long>>() {
            @Override
            public Tuple2<Long, Long> map(Tuple2<Long, Long> value) { return value; }
        })
        .withForwardedFields("0;1")
        .groupBy(0)
        .reduceGroup(new GroupReduceFunction<Tuple2<Long, Long>, Tuple2<Long, Long>>() {
            @Override
            public void reduce(Iterable<Tuple2<Long, Long>> values, Collector<Tuple2<Long, Long>> out) {}
        })
        .withCombineHint(CombineHint.HASH)
        .output(new DiscardingOutputFormat<>());
    
    Plan plan = env.createProgramPlan();
    OptimizedPlan optimizedPlan = TestCompilerUtils.compileOptimizer(plan);
    
    for (PlanNode node : optimizedPlan.getAllNodes()) {
        if (node instanceof SingleInputPlanNode) {
            SingleInputPlanNode singleInputNode = (SingleInputPlanNode) node;
            if (singleInputNode.getProgramOperator() instanceof GroupReduceOperatorBase) {
                assertEquals(
                    ShipStrategyType.PARTITION_HASH,
                    singleInputNode.getInput().getShipStrategy()
                );
            }
        }
    }
}
```

## Example: Incorrect test (would miss the bug)

```java
// WRONG: Only checks that strategy is not null, not that it's PARTITION_HASH
assertNotNull(singleInputNode.getInput().getShipStrategy());

// WRONG: Uses OPTIMIZER_CHOOSES which does NOT trigger the bug
.withCombineHint(CombineHint.OPTIMIZER_CHOOSES)

// WRONG: Doesn't include a MapOperator, so the partition pushdown doesn't get blocked
input.groupBy(0).reduceGroup(...)
```