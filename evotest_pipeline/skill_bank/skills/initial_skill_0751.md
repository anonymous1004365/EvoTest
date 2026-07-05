---
name: mini-accumulo-cluster-stop-idempotency
description: When testing a MiniAccumuloCluster stop() method, verify that calling
  stop() multiple times is safe and does not throw exceptions. This skill also applies
  to any lifecycle manager where double-stop might cause NullPointerException or IllegalStateException.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# mini-accumulo-cluster-stop-idempotency

## Instructions

# MiniAccumuloCluster Stop Idempotency

## Instructions

- WHEN the TG encounters a `stop()` method on an object that manages external processes (such as MiniAccumuloCluster managing ZooKeeper and Accumulo processes)
- THEN it should write a test that calls `stop()` **multiple times** (e.g., twice in sequence) and verifies that the second call completes without throwing any exception (NullPointerException, IOException, InterruptedException, etc.)
- Include a concrete test where:
  1. A MiniAccumuloCluster-like instance is started
  2. `stop()` is called once
  3. `stop()` is called again
  4. Assert that the second `stop()` succeeds (no exception thrown)
- The test should verify that internal state (e.g., references to subprocess objects) is properly nulled/cleared after the first `stop()` so the second `stop()` does not attempt to operate on null references.
- Common pitfalls:
  - Testing only that `stop()` can be called once successfully
  - Forgetting that internal Process references may be set to `null` after the first `stop()`, making subsequent calls attempt to invoke `.destroy()` or `.waitFor()` on null
  - Assuming that guard conditions (e.g., `if (process != null)`) already exist when they may not
  - Not starting the service before stopping it (the test must go through the normal lifecycle: start → stop → stop)

### Example (correct approach):

```java
@Test
public void multipleStopsIsAllowed() throws Exception {
    MiniAccumuloCluster cluster = new MiniAccumuloCluster(config);
    cluster.start();
    cluster.stop();
    cluster.stop();  // second stop must not throw NullPointerException
}
```

### Example (incorrect approach — would miss the bug):

```java
@Test
public void stopWorksOnce() throws Exception {
    MiniAccumuloCluster cluster = new MiniAccumuloCluster(config);
    cluster.start();
    cluster.stop();
    // Only tests single-stop; a second stop might NPE
}
```