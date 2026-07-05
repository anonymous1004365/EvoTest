---
name: execution-config-serialization-null-handling
description: When transferring ExecutionConfig between a StreamGraph and a JobGraph,
  the serialization step can produce a null/empty ExecutionConfig, causing a NullPointerException
  downstream. This skill teaches how to test that the execution config is correctly
  set and deserialized on the resulting JobGraph.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
- VALIDATION
- SERIALIZATION_CONFIG_TRANSFER
test_pattern: STATE_TEST
---

# execution-config-serialization-null-handling

## Instructions

# ExecutionConfig Serialization and Transfer Between Graph Stages

## Instructions

- WHEN the TG encounters code that retrieves an `ExecutionConfig` from a `StreamGraph` (via `streamGraph.getExecutionConfig()`) and passes it to `JobGraph.setExecutionConfig(ExecutionConfig)` (which throws `IOException`), THEN the TG should write a test that:
  1. Creates a `StreamExecutionEnvironment` (or `StreamGraph`) with a non-default `ExecutionConfig` (e.g., set an explicit parallelism value, enable object reuse, or add a registered type).
  2. Calls the method that transfers the config from `StreamGraph` to `JobGraph` (e.g., `StreamingJobGraphGenerator.createJobGraph()`).
  3. Retrieves the resulting `JobGraph` and calls `jobGraph.getExecutionConfig()`.
  4. Verifies that the retrieved `ExecutionConfig` is not null AND that it preserves the non-default settings that were originally configured.
  
- WHEN `JobGraph.getExecutionConfig()` returns null or throws a `NullPointerException` during test assertions, THEN the test should fail with a clear message indicating that the execution config was not properly serialized/deserialized during graph construction.

- WHEN the serialization path goes through `ExecutionConfig.clone()` or Java serialization (e.g., via `writeObject`/`readObject`), THEN test that all custom settings survive the round trip — not just basic fields like `setParallelism()` but also registered types, Kryo registrations, global job parameters, and execution mode flags.

- Common pitfalls to avoid:
  - **Testing only one config setting**: A test that only calls `jobGraph.getExecutionConfig()` and checks it's non-null is insufficient. Verify at least one specific config value (e.g., `isObjectReuseEnabled()`, `getParallelism()`) matches the original.
  - **Ignoring the `IOException`**: `JobGraph.setExecutionConfig()` throws `IOException`. Ensure the test method properly declares or catches this exception rather than wrapping it silently.
  - **Testing with null config**: Do NOT test by passing a null `ExecutionConfig` — the bug is that the serialized (non-null) config produces a null or empty result on deserialization, not that null input is handled.
  - **Not checking the `JobGraph` after construction**: The config transfer happens inside graph generation. Call `getExecutionConfig()` on the *resulting JobGraph*, not on the original `StreamExecutionEnvironment`.

### Example (correct — catches the NullPointerException bug):

```java
@Test
public void testExecutionConfigTransferredToJobGraph() throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.setParallelism(42);
    env.getConfig().enableObjectReuse();
    
    StreamGraph streamGraph = env.getStreamGraph();
    // streamGraph.setJobName(...) if needed
    streamGraph.setChaining(false); // or other settings

    JobGraph jobGraph = StreamingJobGraphGenerator.createJobGraph(streamGraph);
    ExecutionConfig jobConfig = jobGraph.getExecutionConfig();
    
    assertNotNull("ExecutionConfig should not be null on JobGraph", jobConfig);
    assertEquals("Parallelism should be preserved after serialization", 
        42, jobGraph.getJobConfiguration().getInteger(ExecutionConfigOptions.PARALLELISM_DEFAULT, -1));
    assertTrue("Object reuse should be enabled after serialization", 
        jobConfig.isObjectReuseEnabled());
}
```

### Example (incorrect — does not verify the fix):

```java
@Test
public void testExecutionConfig() throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    StreamGraph streamGraph = env.getStreamGraph();
    JobGraph jobGraph = StreamingJobGraphGenerator.createJobGraph(streamGraph);
    // WRONG: This passes even if getExecutionConfig() returns null,
    // because it doesn't call any method on the result.
    ExecutionConfig config = jobGraph.getExecutionConfig();
    
    // WRONG: Only checking non-null without verifying specific values
    // may allow a deserialized empty/default config to pass
    assertNotNull(config);
}
```