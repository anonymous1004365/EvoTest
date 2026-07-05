---
name: stateful-operator-failure-isolation
description: When testing stateful operators that checkpoint/restore state, write
  tests that verify failure isolation — a failure in one operator should not corrupt
  the state or execution of other operators in the same job. Use when operator state
  is shared or checkpointed across parallel tasks.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
- VALIDATION
test_pattern: STATE_TEST
---

# stateful-operator-failure-isolation

## Instructions

# Stateful Operator Failure Isolation

## Instructions

- WHEN the TG encounters a stateful operator that performs checkpointing or state serialization/deserialization (e.g., operators extending `RichFunction` with `CheckpointedFunction` or using `ValueState`, `ListState`, etc.)
- THEN the TG should write a parameterized or scenario-based test that:
  1. Creates a Flink mini-cluster (`MiniClusterWithClientResource`) or uses `StreamExecutionEnvironment` in local mode.
  2. Constructs a job DAG with **two or more parallel stateful operators** (e.g., two `KeyedProcessFunction` or `RichMapFunction` instances using keyed state).
  3. Injects a controlled failure in **one of the operators** (e.g., by throwing a `RuntimeException` during `processElement` or `snapshotState`) while the other operator(s) remain healthy.
  4. Asserts that the **healthy operator's state is correctly checkpointed/restored** and produces correct results despite the failure in the sibling operator.
  5. Verifies the **job eventually fails** or recovers depending on the restart strategy, but the **healthy operator's partial results do not leak into or corrupt** the failing operator's state.

- Include concrete type usage: for keyed state, use `ValueStateDescriptor<Long>` with `TypeInformation.of(Long.class)`, and for operator state use `ListStateDescriptor<String>` with `Types.STRING`.

- Common pitfalls to avoid:
  - ❌ Testing only a single operator in isolation — this misses cross-operator state corruption bugs.
  - ❌ Assuming operator state is fully independent — test that a failure in one parallel subtask does not corrupt the state partition of another subtask.
  - ❌ Not verifying the *output* of the healthy operator after the failure — the bug manifests when successful operators produce incorrect results or fail silently.
  - ❌ Using `enableCheckpointing()` but not calling `executeAndWaitForCompletion()` or similar synchronous execution that exposes checkpoint failures.

- **Correct example (Java)**:
  ```java
  @Test
  public void testTwoStatefulOperatorsFailureIsolation() throws Exception {
      StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
      env.setParallelism(2);
      env.enableCheckpointing(100);
      
      DataStream<Long> source = env.fromElements(1L, 2L, 3L, 4L, 5L);
      
      DataStream<Long> transformed = source
          .keyBy(x -> x % 2)
          .process(new HealthyStatefulOperator())
          .keyBy(x -> x % 2)
          .process(new FailingStatefulOperator());
      
      List<Long> results = transformed.executeAndCollect(5000);
      
      // Verify that healthy operator's output reaches the sink despite failure in sibling
      assertThat(results).contains(1L, 2L, 3L, 4L, 5L);
  }
  ```

- **Incorrect example (what the buggy test might look like)**:
  ```java
  @Test
  public void testOperatorInIsolation() throws Exception {
      // Only tests one operator — misses cross-operator state interaction
      HealthyStatefulOperator op = new HealthyStatefulOperator();
      op.open(new Configuration());
      op.processElement(1L, ctx, out);
      // No checkpointing, no parallel sibling
  }
  ```