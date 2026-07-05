---
name: abandoned-cluster-id-reuse
description: When testing cluster node recovery where a node is disposed and restarted
  with an active-but-in-future lease record, the TG should verify that the existing
  cluster ID is reused rather than a new one being generated. Apply this skill when
  dealing with cluster node lifecycle and orphaned lease records.
code_tags:
- STATE_MUTATION
- CONCURRENCY
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# abandoned-cluster-id-reuse

## Instructions

# Abandoned Cluster ID Reuse

## Instructions

- WHEN the TG encounters a cluster node lifecycle scenario where a `DocumentNodeStore` is disposed and a new instance is created with the same `DocumentStore` (e.g., simulating a restart/crash recovery with orphaned lease records),
- THEN the TG should:
  1. Create a first `DocumentNodeStore` using `new DocumentMK.Builder().setDocumentStore(mem).clock(clock).setAsyncDelay(0).setLeaseCheck(false).getNodeStore()` and record its `getClusterId()`.
  2. Dispose the first `DocumentNodeStore` via `ns1.dispose()`.
  3. Before creating the second instance, modify the cluster node record to simulate an "active" state with a lease end time **in the future** using an `UpdateOp` that sets `ClusterNodeInfo.STATE` to `ClusterNodeState.ACTIVE.toString()` and `ClusterNodeInfo.LEASE_END_KEY` to `now + waitFor` (e.g., `now + 2000`), then `findAndUpdate` on `Collection.CLUSTER_NODES`.
  4. Create a second `DocumentNodeStore` with the same builder configuration (same `DocumentStore`, same `clock`).
  5. Assert that the second instance's `getClusterId()` equals the **original** cluster ID — not a new/generated one: `assertEquals("should have re-used existing cluster id", cid, ns1.getClusterId())`.
  6. Use a `Clock.Virtual` to control time precisely and avoid real-time delays.

- **Common pitfalls:**
  - ❌ Not updating the lease end time to be in the future before restarting — the record's lease will appear expired and the new instance will correctly generate a new ID, making it impossible to detect the bug.
  - ❌ Using `new DocumentMK.Builder()` without passing the same `clock` instance — the internal clock may not be synchronized with the virtual time, causing lease checks to behave differently.
  - ❌ Forgetting to call `ClusterNodeInfo.setClock(clock)` or pass `.clock(clock)` to the builder — without this, the virtual clock won't be used for time calculations.
  - ❌ Testing only with a clean state (no orphaned record) — the bug only manifests when an abandoned-but-still-active lease record exists in the document store.
  - ❌ Setting `setLeaseCheck(true)` (the default) — lease checks may interfere with the test scenario; use `setLeaseCheck(false)`.

- **Correct example:**
```java
@Test
public void useAbandoned() throws InterruptedException {
    Clock clock = new Clock.Virtual();
    clock.waitUntil(System.currentTimeMillis());
    ClusterNodeInfo.setClock(clock);
    MemoryDocumentStore mem = new MemoryDocumentStore();

    DocumentNodeStore ns1 = new DocumentMK.Builder().
            setDocumentStore(mem).
            clock(clock).
            setAsyncDelay(0).
            setLeaseCheck(false).
            getNodeStore();

    DocumentStore ds = ns1.getDocumentStore();
    int cid = ns1.getClusterId();

    ClusterNodeInfoDocument cnid = ds.find(Collection.CLUSTER_NODES, "" + cid);
    assertNotNull(cnid);
    assertEquals(ClusterNodeState.ACTIVE.toString(), cnid.get(ClusterNodeInfo.STATE));
    ns1.dispose();

    long waitFor = 2000;
    // modify record to indicate "active" with a lease end in the future
    UpdateOp up = new UpdateOp("" + cid, false);
    up.set(ClusterNodeInfo.STATE, ClusterNodeState.ACTIVE.toString());
    long now = clock.getTime();
    up.set(ClusterNodeInfo.LEASE_END_KEY, now + waitFor);
    ds.findAndUpdate(Collection.CLUSTER_NODES, up);

    // try restart
    ns1 = new DocumentMK.Builder().
            setDocumentStore(mem).
            clock(clock).
            setAsyncDelay(0).
            setLeaseCheck(false).
            getNodeStore();
 
    assertEquals("should have re-used existing cluster id", cid, ns1.getClusterId());
    ns1.dispose();
}
```

- **Incorrect example (would not catch the bug):**
```java
@Test
public void useAbandoned_Wrong() throws InterruptedException {
    Clock clock = new Clock.Virtual();
    clock.waitUntil(System.currentTimeMillis());
    ClusterNodeInfo.setClock(clock);
    MemoryDocumentStore mem = new MemoryDocumentStore();

    DocumentNodeStore ns1 = new DocumentMK.Builder().
            setDocumentStore(mem).
            clock(clock).
            setAsyncDelay(0).
            setLeaseCheck(false).
            getNodeStore();

    int cid = ns1.getClusterId();
    ns1.dispose();

    // BUG: No UpdateOp to simulate orphaned active lease with future end time
    // Without this, the new instance will see an expired/inactive record
    // and generate a NEW cluster ID instead of reusing the old one

    ns1 = new DocumentMK.Builder().
            setDocumentStore(mem).
            clock(clock).
            setAsyncDelay(0).
            setLeaseCheck(false).
            getNodeStore();
 
    // This assertion PASSES on fixed code but FAILS on buggy code
    // because without the UpdateOp, both versions generate a new ID
    // So this test would never detect the regression
    assertEquals("should have re-used existing cluster id", cid, ns1.getClusterId());
    ns1.dispose();
}
```