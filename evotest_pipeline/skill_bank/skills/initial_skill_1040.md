---
name: iteration-ship-strategy-pushing
description: WHEN testing optimizer compilation plans involving nested iterations
  (bulk inside delta), THEN verify that partitioning strategies (PARTITION_HASH, FORWARD)
  are correctly pushed through the iteration boundaries. This skill applies to workspace
  optimization tests that inspect ShipStrategyType on Channels of WorksetIterationPlanNode
  and BulkIterationPlanNode.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# iteration-ship-strategy-pushing

## Instructions

# Nested Iteration Ship Strategy Pushing

## Instructions

- WHEN the TG encounters a test that chains a DeltaIteration on top of a BulkIteration (e.g., `doDeltaIteration(bulkResult, edges)` where `bulkResult` comes from `doBulkIteration(...)`)
- THEN the TG should verify that the optimizer correctly pushes hash partitioning (`PARTITION_HASH`) out of the delta iteration into the bulk iteration's step function, by asserting:

  1. `wipn.getInput1().getShipStrategy()` equals `ShipStrategyType.FORWARD` on the `WorksetIterationPlanNode`'s first input channel
  2. For each `Channel c` in `bipn.getRootOfStepFunction().getInputs()`, assert `c.getShipStrategy()` equals `ShipStrategyType.PARTITION_HASH`

- The TG should also verify the TempMode and DataExchangeMode on both inputs:
  - `wipn.getInput1().getTempMode()` == `TempMode.NONE`
  - `wipn.getInput2().getTempMode()` == `TempMode.NONE`
  - `wipn.getInput1().getDataExchangeMode()` == `DataExchangeMode.BATCH`
  - `wipn.getInput2().getDataExchangeMode()` == `DataExchangeMode.BATCH`

- WHEN building the test plan, call `compileNoStats(env.createProgramPlan())` and retrieve the `WorksetIterationPlanNode` from the sink's input source

- Common pitfalls:
  - Testing only the first level of iteration nodes without checking that partitioning strategies are correctly pushed into inner iteration step functions
  - Forgetting to check the ShipStrategyType on `bipn.getRootOfStepFunction().getInputs()` — this is where the hash partitioning should appear after being pushed out of the delta iteration
  - Using `compileWithStats()` instead of `compileNoStats()` — the test must use `compileNoStats` to avoid requiring statistics
  - Not verifying `DataExchangeMode.BATCH` and `TempMode.NONE` on both input channels of the `WorksetIterationPlanNode`

### Correct Example (from `testTwoIterationsDirectlyChained`):
```java
WorksetIterationPlanNode wipn = (WorksetIterationPlanNode) op.getDataSinks().iterator().next().getInput().getSource();
BulkIterationPlanNode bipn = (BulkIterationPlanNode) wipn.getInput1().getSource();

// the hash partitioning has been pushed out of the delta iteration into the bulk iteration
assertEquals(ShipStrategyType.FORWARD, wipn.getInput1().getShipStrategy());

// the input of the root step function is the last operator of the step function
// since the work has been pushed out of the bulk iteration, it has to guarantee the hash partitioning
for (Channel c : bipn.getRootOfStepFunction().getInputs()) {
    assertEquals(ShipStrategyType.PARTITION_HASH, c.getShipStrategy());
}
```

### Incorrect Example (what the buggy test would assert — expects PARTITION_HASH on the delta input instead of FORWARD):
```java
// WRONG: This assertion passes on the buggy version but fails on the fixed version
assertEquals(ShipStrategyType.PARTITION_HASH, wipn.getInput1().getShipStrategy());
// Missing check of bipn.getRootOfStepFunction().getInputs() for PARTITION_HASH
```