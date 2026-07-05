---
name: background-lease-update-thread-lifecycle
description: This skill teaches how to test that background lease update threads are
  properly started and managed by DocumentNodeStore. Use it when testing DocumentNodeStore's
  background operation thread lifecycle, particularly verifying that threads are created
  with the correct cluster ID and remain running.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- BACKGROUND_THREAD_LEASE_UPDATE
- CONCURRENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# background-lease-update-thread-lifecycle

## Instructions

# Background Lease Update Thread Lifecycle Verification

## Instructions

- WHEN testing `DocumentNodeStore` background operations, specifically the `BackgroundLeaseUpdate` inner class (a `NodeStoreTask`):
  - THEN the TG should verify that a background lease update thread is actually running after the store is created, using `DocumentNodeStoreTest.backgroundLeaseUpdateThreadRunning(int clusterId)` or equivalent thread inspection via `ThreadMXBean`.
  - Use `ManagementFactory.getThreadMXBean()` to enumerate threads and check that a thread whose name contains `"DocumentNodeStore lease update thread"` and the given cluster ID exists and is in `RUNNABLE` state.
  - Do NOT just verify the store is not null or that `runBackgroundOperations()` returns without error — these do NOT validate that the background thread was actually started.
  - Test with at least two cluster nodes (cluster IDs 1 and 2) to catch per-cluster-node threading issues.
  - The test should create a `DocumentNodeStore` via `DocumentMKBuilderProvider`, and immediately check that the background lease update thread for that cluster ID is running.
  - Common pitfall: Only testing that `getNodeStore()` returns a non-null object, then calling `runBackgroundOperations()`, without checking that the dedicated background thread was actually spawned and is alive.

### Correct approach (Java/JUnit example):
```java
@Test
public void testBackgroundLeaseUpdateThread() throws Exception {
    DocumentNodeStore store = builderProvider.newBuilder()
            .setAsyncDelay(0)
            .getNodeStore();
    int clusterId = store.getClusterId();
    assertTrue("Lease update thread for cluster " + clusterId + " must be running",
            backgroundLeaseUpdateThreadRunning(clusterId));
}
```

### Incorrect approach (what to avoid):
```java
@Test
public void testBackgroundLeaseUpdateThread() throws Exception {
    DocumentNodeStore store = builderProvider.newBuilder()
            .setAsyncDelay(0)
            .getNodeStore();
    assertNotNull("store should not be null", store);
    store.runBackgroundOperations(); // this does NOT verify the thread lifecycle
}
```