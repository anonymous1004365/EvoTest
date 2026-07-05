---
name: wal-gc-scan-servers-old-style
description: When testing WAL garbage collection logic, the TG should verify that
  old-style `scanServers()` calls are properly replaced with `getCurrentServers()`.
  The bug is that calling `scanServers()` on a mock LiveTServerSet causes unexpected
  side effects (like adding servers to the internal cache), leading to incorrect GC
  behavior where logs are not deleted when they should be.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# wal-gc-scan-servers-old-style

## Instructions

# WAL Garbage Collection: Use `getCurrentServers()` Instead of `scanServers()`

## Instructions

- WHEN the TG encounters a `LiveTServerSet` that is used in `GarbageCollectWriteAheadLogs` WAL garbage collection logic
- THEN the TG should verify that the test uses `EasyMock.expect(tserverSet.getCurrentServers()).andReturn(...)` (the "old style" pattern), and NOT `scanServers()` (which was the buggy old-style approach that had side effects)
- WHEN the TG sees a test calling `tserverSet.getCurrentServers()` returning a set of current `TServerInstance` objects, THEN it should verify the test correctly expects exactly the right set of servers, especially when a server has a different session ID (e.g., `currentServer = "localhost:1234[SESSION]"` vs `oldServer = "localhost:1234[OTHERSESS]"`)
- WHEN setting up a test scenario where a WAL was created on a previous tserver session (different session ID but same host:port), THEN the TG should verify that:
  1. The `getAllMarkers()` returns markers keyed by the old server (e.g., `markers2` keyed by `oldServer`)
  2. The `getCurrentServers()` returns the current live servers (e.g., `currentServer`)
  3. The expected behavior is that the WAL from the dead session should be garbage collected (deleted)
- WHEN verifying deletions, THEN the TG should assert that `fs.deleteRecursively(path)` is called for unreferenced WALs from dead servers
- Common pitfall: using `scanServers()` on a mock `LiveTServerSet` instead of `getCurrentServers()` — this is the buggy old-style approach. `scanServers()` has side effects (it modifies internal ZooKeeper state), so tests should use `getCurrentServers()` which returns the current cached set without side effects.

### Correct Example (simplified)
```java
// Setup: the old server's WAL should be GC'd when currentServer is the only live server
EasyMock.expect(tserverSet.getCurrentServers()).andReturn(Collections.singleton(currentServer));
EasyMock.expect(marker.getAllMarkers()).andReturn(markers2).once(); // markers keyed by oldServer
EasyMock.expect(marker.state(oldServer, id)).andReturn(new Pair<>(WalState.OPEN, path));
EasyMock.expect(fs.deleteRecursively(path)).andReturn(true).once();
```

### Incorrect Example (buggy pattern)
```java
// WRONG: Calling scanServers() triggers side effects
// scanServers() is an old-style method that modifies state
// Expected result: 1 deletion, but got 2 because scanServers() re-reads state
```