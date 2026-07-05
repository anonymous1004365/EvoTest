---
name: filesystem-null-path-npe
description: When testing FileSystem operations that call listStatus() on a non-existent
  or invalid path, listStatus() may return null. The test should verify the source
  function handles this gracefully without throwing a NullPointerException.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# filesystem-null-path-npe

## Instructions

# Null Pointer on FileSystem.listStatus() Returned Null

## Instructions

- WHEN the TG encounters a method that calls `FileSystem.listStatus(Path)` and then iterates over the returned `FileStatus[]` array **without** a null check before the loop
- THEN the TG should write a test that passes a path which does not exist or is malformed (e.g., `"?non-existing-path"`) to trigger a null return from `listStatus()`
- The test should verify that calling `run()` on the source does **not** throw a `NullPointerException` — instead, the method should log a warning and continue gracefully
- The test should call `cancel()` from another thread after a short sleep (e.g., 1000ms) to stop the infinite loop in `run()`, otherwise the test will hang
- **Common pitfall**: Testing only with valid, existing paths. This misses the null-return scenario entirely.
- **Common pitfall**: Forgetting to cancel the running source function from another thread, causing the test to run forever.

### Correct Example (test passes on fixed code, fails on buggy code with NPE)

```java
@Test
public void testForEmptyLocation() throws Exception {
    final FileMonitoringFunction fileMonitoringFunction =
            new FileMonitoringFunction("?non-existing-path", 1L, FileMonitoringFunction.WatchType.ONLY_NEW_FILES);

    new Thread() {
        @Override
        public void run() {
            try {
                Thread.sleep(1000L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            fileMonitoringFunction.cancel();
        }
    }.start();

    fileMonitoringFunction.run(
            new SourceFunction.SourceContext<Tuple3<String, Long, Long>>() {
                @Override
                public void collect(Tuple3<String, Long, Long> element) {}
                @Override
                public void collectWithTimestamp(Tuple3<String, Long, Long> element, long timestamp) {}
                @Override
                public void emitWatermark(Watermark mark) {}
                @Override
                public void markAsTemporarilyIdle() {}
                @Override
                public Object getCheckpointLock() { return null; }
                @Override
                public void close() {}
            });
}
```

### Incorrect Example (misses the bug)

```java
@Test
public void testValidPath() throws Exception {
    // Only tests with a valid path — the null listStatus() scenario is never hit
    final FileMonitoringFunction fileMonitoringFunction =
            new FileMonitoringFunction("/tmp/valid-path", 1L, FileMonitoringFunction.WatchType.ONLY_NEW_FILES);
    // ... test runs without NPE but doesn't cover the bug
}
```