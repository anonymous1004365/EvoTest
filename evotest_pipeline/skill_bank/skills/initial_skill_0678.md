---
name: mapred-input-format-test-isolation
description: When testing Hadoop mapred InputFormat subclasses that connect to external
  services (ZooKeeper), the test must initialize or mock the connection state before
  creating splits/readers, and must clean up resources to prevent cascading failures
  across tests. Use this skill when writing unit tests for AccumuloInputFormat, AccumuloRowInputFormat,
  or similar InputFormat implementations.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# mapred-input-format-test-isolation

## Instructions

# MapRed InputFormat Test Isolation

## Instructions

- WHEN the TG encounters a test for a Hadoop `mapred` (org.apache.hadoop.mapred) `InputFormat` subclass such as `AccumuloRowInputFormat`, `AccumuloInputFormat`, or `AccumuloMultiTableInputFormat` — specifically a test that invokes `getSplits()` or constructs a `RecordReader` via `getRecordReader()`
- THEN the TG MUST ensure that the test properly initializes the ZooKeeper connection configuration (e.g., `ClientConfiguration` or `ZooKeeperInstance`) before calling `InputFormat.getSplits()` or `getRecordReader()`. The test MUST also verify that a `RuntimeException` containing `"Failed to connect to zookeeper"` is NOT thrown when a valid configuration is set. If the test is a mock/unit test (no real ZooKeeper), it MUST either mock the ZooKeeper dependency or wrap the call in an `assertThrows` expecting the connection failure exception.

- WHEN the TG writes a test for the `AccumuloRowInputFormat` or similar mapred InputFormat that sets `InputFormatBase` configuration options (e.g., via `InputConfigurator`, `setInputInfo`, `setZooKeeperInstance`, `setScanAuthorizations`, or `setRanges`)
- THEN the TG MUST verify that the test calls `InputFormat.getSplits(jobConf, numSplits)` after setting the configuration, because `getSplits()` triggers ZooKeeper/tablet locator initialization and is the point where connection failures manifest. The test should expect `getSplits()` to either succeed with proper config or throw a `RuntimeException` wrapping a ZooKeeper connection error otherwise.

- WHEN the TG writes a test for a `mapred` (not `mapreduce`) InputFormat that internally calls `getSplits()` which attempts to connect to ZooKeeper
- THEN the TG MUST NOT assume that an empty or default `JobConf` suffices — the test must explicitly set ZooKeeper connection info (via `setZooKeeperInstance`) or else `getSplits()` will throw `RuntimeException: Failed to connect to zookeeper`. Test isolation between successive test methods is also critical: shared static state (e.g., `Connector`, `Instance`, cached tablet locators) can cause tests to interfere with each other (order dependency). Use `@Before` / `@After` to reset or reinitialize state per test.

### Common Pitfalls
1. **Testing only the `mapreduce` API but not the `mapred` API**: The bug exists in the `mapred` package, which uses `JobConf` and `InputSplit[]` (not `List<InputSplit>`). Write tests for BOTH packages.
2. **Ignoring ZooKeeper connection failures**: Do not assume ZooKeeper is running in unit tests — either mock it, or intentionally test that the proper exception is thrown when no connection is configured, AND test that valid configuration makes the exception go away (if ZooKeeper is available, e.g. in integration tests).
3. **Using `@Test` without isolation**: If the test stores static cached data (e.g., cached tablet locators), the first test may perform the connection and succeed, while subsequent tests re-use cached state and appear to pass — masking bugs that only appear when cache is cold. Use fresh `JobConf` and fresh InputFormat instance for each test.
4. **Testing only the constructor or trivial methods**: The critical code path is `getSplits()` which initializes tablet locators and connects to ZooKeeper. Make sure your tests exercise that method.

### Correct Test Pattern (mapred package, expecting connection failure without config)

```java
@Test
public void testGetSplitsWithoutConfigThrows() throws IOException {
    AccumuloRowInputFormat format = new AccumuloRowInputFormat();
    JobConf job = new JobConf();
    // Intentionally NOT setting ZooKeeper instance
    assertThrows(RuntimeException.class, () -> format.getSplits(job, 1),
        "Expected RuntimeException when ZooKeeper is not configured");
}
```

### Incorrect Test Pattern

```java
// BAD: Only tests wrapping in getRecordReader() without testing getSplits()
// BAD: Uses same static JobConf across tests causing order dependency
// BAD: Does not test the mapred package at all (only tests mapreduce)
@Test
public void testBadPattern() throws IOException {
    AccumuloRowInputFormat format = new AccumuloRowInputFormat();
    JobConf job = new JobConf();
    // This line might succeed if cached from a previous test,
    // masking the bug. Even if it fails, we haven't tested getSplits().
    InputSplit[] splits = format.getSplits(job, 1); // fragile / order-dependent
}
```

### Correct Test Pattern (with valid config, if ZooKeeper available — integration test)

```java
@Test
public void testGetSplitsWithValidConfig() throws IOException {
    AccumuloRowInputFormat format = new AccumuloRowInputFormat();
    JobConf job = new JobConf();
    // Configure ZooKeeper connection
    InputFormatBase.setZooKeeperInstance(job, ClientConfiguration.create()
        .withInstance("myInstance")
        .withZkHosts("localhost:2181"));
    InputFormatBase.setInputInfo(job, "user", "password".getBytes(),
        "tableName", new Authorizations());
    // Now getSplits should attempt to connect to ZooKeeper
    // In a unit test without ZooKeeper, this would still throw,
    // but the key is that we ARE testing the code path
    InputSplit[] splits = format.getSplits(job, 10);
    assertNotNull(splits);
}
```