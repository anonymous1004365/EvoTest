---
name: stats-collector-method-invocation-verification
description: Teaches TG to verify that stats collector methods receive the correct
  metric values when background read/write operations are performed, using both unit-level
  and integration-level testing patterns.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# stats-collector-method-invocation-verification

## Instructions

# Stats Collector Method Invocation Verification

## Instructions

- WHEN the TG encounters a class that delegates metric or statistics collection to a `DocumentNodeStoreStatsCollector` (or similar stats collector interface) via methods like `doneBackgroundRead(BackgroundReadStats)`, `doneBackgroundUpdate(BackgroundWriteStats)`, `doneMerge(int, long, boolean, boolean)`, or `failedMerge(int, long, boolean, boolean)`
- THEN the TG should write a test that:
  1. Creates a stats collector mock using `mock(DocumentNodeStoreStatsCollector.class)`
  2. Sets up a `DocumentNodeStore` via `DocumentMKBuilderProvider` with `.setNodeStoreStatsCollector(mockCollector)` and calls the relevant operations (e.g., `runBackgroundReadOperations()`, `runBackgroundUpdateOperations()`, `merge(...)`)
  3. Verifies that the mocked stats collector's method was invoked with the expected argument types using `verify(mockCollector).methodName(any(...))`
  4. For unit-level tests (like `DocumentNodeStoreStatsTest`), directly create `BackgroundReadStats` and `BackgroundWriteStats` objects, set their numeric fields (`numExternalChanges`, `num`), call `doneBackgroundRead(readStats)` / `doneBackgroundUpdate(writeStats)` on `DocumentNodeStoreStats`, and assert that the underlying `Meter`/`Histogram`/`Timer` from `MetricStatisticsProvider` recorded the correct count via `assertEquals(expectedCount, getMeter(METRIC_NAME).getCount())`

- WHEN verifying specific metric values in unit tests on `DocumentNodeStoreStats`:
  - Test `backgroundRead()` by: creating a `BackgroundReadStats`, setting `readStats.numExternalChanges = 5`, calling `stats.doneBackgroundRead(readStats)`, then asserting `assertEquals(5, getMeter(DocumentNodeStoreStats.BGR_NUM_CHANGES_RATE).getCount())`
  - Test `backgroundWrite()` by: creating a `BackgroundWriteStats`, setting `writeStats.num = 7`, calling `stats.doneBackgroundUpdate(writeStats)`, then asserting `assertEquals(7, getMeter(DocumentNodeStoreStats.BGW_NUM_WRITES_RATE).getCount())`

- WHEN using integration tests with `DocumentMKBuilderProvider` and mock collector:
  - Ensure `setAsyncDelay(0)` to make background operations run synchronously
  - Call `setMaxBackOffMillis(0)` to disable retries on failed merges
  - Use `any(BackgroundReadStats.class)` / `any(BackgroundWriteStats.class)` matchers since exact stats objects are constructed internally
  - For `doneMerge`, verify with `eq(0)` for retry count, `anyLong()` for time, and exact `eq(false)` / `eq(true)` for boolean flags
  - For `failedMerge`, verify it is called twice: once with `eq(false)` for exclusive, once with `eq(true)` for exclusive (due to retry with exclusive lock)

- Common pitfalls to avoid:
  - Do NOT test `DocumentNodeStoreStats` in isolation without a `StatisticsProvider` backed by a real `MetricStatisticsProvider` — the `getMeter(name)` lookup will otherwise return null
  - Do NOT forget to `@After` close/destroy resources: `statsProvider.close()` and `new ExecutorCloser(executor).close()` to avoid thread leaks
  - Do NOT assume `doneBackgroundRead` and `doneBackgroundUpdate` use the same metric names — `BGR_NUM_CHANGES_RATE` is `"DOCUMENT_NS_BGR_NUM_CHANGES_RATE"` while `BGW_NUM_WRITES_RATE` is `"DOCUMENT_NS_BGW_NUM_WRITE_RATE"` (note the singular `WRITE_RATE` vs `WRITES_RATE`)
  - Do NOT verify with exact `BackgroundReadStats`/`BackgroundWriteStats` objects in integration tests (since the framework constructs them internally) — use `any(Class.class)` matchers
  - Do NOT forget to call both `doneMerge(eq(0), anyLong(), eq(false), eq(false))` and `failedMerge(anyInt(), anyLong(), eq(false), eq(false))` + `failedMerge(anyInt(), anyLong(), eq(false), eq(true))` when testing merge failure scenarios

- Example (correct unit test pattern):
```java
@Test
public void backgroundRead() throws Exception {
    BackgroundReadStats readStats = new BackgroundReadStats();
    readStats.numExternalChanges = 5;
    stats.doneBackgroundRead(readStats);
    assertEquals(5, getMeter(DocumentNodeStoreStats.BGR_NUM_CHANGES_RATE).getCount());
}
```

- Example (correct integration test pattern):
```java
@Test
public void doneBackgroundRead() throws Exception {
    nodeStore.runBackgroundReadOperations();
    verify(statsCollector).doneBackgroundRead(any(BackgroundReadStats.class));
}
```

- Example (incorrect — never do this):
```java
// WRONG: Mocking StatisticsProvider loses real metric behavior
@Test
public void backgroundRead_bad() {
    BackgroundReadStats readStats = new BackgroundReadStats();
    readStats.numExternalChanges = 5;
    // No real StatisticsProvider — getMeter will return null!
    stats.doneBackgroundRead(readStats);
    assertEquals(5, getMeter(DocumentNodeStoreStats.BGR_NUM_CHANGES_RATE).getCount()); // NullPointerException!
}
```