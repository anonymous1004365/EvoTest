---
name: standby-sync-cleanup-resource-lifecycle
description: Detects bugs where standby sync clients fail to properly cleanup/disconnect
  when exhausted, leading to resource leaks or connection hangs in the sync loop.
  Apply when testing loop-based client-server sync operations that invoke a `cleanup()`
  method.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
- CONCURRENCY
test_pattern: INTERACTION_TEST
---

# standby-sync-cleanup-resource-lifecycle

## Instructions

# Standby Sync Cleanup Resource Lifecycle

## Instructions

- WHEN the TG encounters a standby sync mechanism where a client communicates with a server in a loop (e.g., a `while (!exhausted)` or `while (running)` loop), and the client has a `cleanup()` (or `cleanupAndRemove()`) method designed to release resources or signal completion to the server
- THEN the TG should write an interaction test that:
  1. Simulates the client executing a full sync cycle — entering the loop, performing at least one sync iteration, and then exiting (e.g., when the client becomes exhausted or is told to stop)
  2. Verifies that after the loop exits, the `cleanup()` method is **actually called** and that its effects are observable (e.g., a resource/file is closed, a connection is released, or a server-side state changes)
  3. For the buggy version: expect that cleanup does NOT happen when it should (e.g., the client's loop terminates without calling cleanup, leaving a stale connection or orphaned resource). Verify this by checking that the server-side is still bound/holding a connection after the client finishes
  4. Uses a real or mock server to verify the state transition (e.g., server no longer sees the client as registered, or a port becomes free) — not just that the client terminated without error
- Include concrete values: the test should mirror the production flow's client/server setup exactly (same host, port, store paths, timeouts)
- **Common pitfalls to avoid**:
  - Testing that only the client exits without hanging (i.e., a timeout test) — the bug is about cleanup, not just termination
  - Not connecting the client to a real server — without a server, cleanup effects cannot be observed
  - Relying on `verify(cleanup, times(1))` on a mock client — the TG must test the *actual* cleanup side-effect (server-side unbinding, resource release, etc.)
  - Testing only a clean, single-cycle sync — test multi-cycle or edge-condition exits (e.g., exhausted flag set mid-loop, interrupt, or error condition) to flush out the missing cleanup call

### Correct approach example
```java
// Setup server and client as in production
server.start();
client.start();
// Perform one full sync
while (!exhausted) {
    client.runSyncCycle(); // or similar
    if (firstCycleDone) break;
}
client.stop();   // triggers loop exit
// After stop, verify cleanup happened:
assertFalse("Server should have released the client after cleanup", server.isClientBound(clientId));
// Or verify a port/file is freed
```

### Incorrect approach example
```java
// WRONG: only tests that client exits, not that cleanup happens
client.start();
Thread.sleep(5000); // wait for timeout
assertFalse("Client should have stopped", client.isRunning());
// Missing: checking that server released the client
```