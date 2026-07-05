---
name: zookeeper-node-race-condition-testing
description: When testing code that watches ZooKeeper nodes for changes, the TG should
  simulate race conditions where nodes disappear between listing and watching to verify
  proper KeeperException handling and retry logic.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: INTERACTION_TEST
---

# zookeeper-node-race-condition-testing

## Instructions

# ZooKeeper Node Race Condition Testing

## Instructions

- WHEN the TG encounters code that performs a ZooKeeper `getChildren` (or similar listing) on a path and then processes individual nodes by checking their existence or setting watches (e.g., via `exists`, `getData`, or another `getChildren`)
- THEN the TG should write a test that simulates the race condition where a node returned by `getChildren` is deleted (or its parent is deleted) before the follow-up ZooKeeper operation completes
  - Use a mocking framework (e.g., Mockito) to create a `ZooKeeper` mock or spy
  - Make the first call to `getChildren` return a non-empty list of child paths
  - Make the follow-up call (e.g., `exists`, `getData`, `getChildren`) throw a `KeeperException.NoNodeException` (or `KeeperException` with `Code.NONODE`)
  - Verify that the code under test handles this exception gracefully (e.g., logs a warning, continues processing remaining nodes, does not crash)

- WHEN the TG tests a `Watcher` callback that processes ZooKeeper events of type `Event.EventType.NodeDeleted` or `Event.EventType.NodeChildrenChanged`
- THEN the TG should verify that the watcher does not assume the node still exists when the callback fires — a common race is that between receiving the event and reading the node's data, the node has been deleted
  - The test should configure the mock ZooKeeper to throw `KeeperException.NoNodeException` on the data-read operation inside the `process` method
  - Verify the watcher catches the exception and does not propagate it

- **Common pitfalls:**
  - Testing only the "happy path" where all ZooKeeper operations succeed — this misses the critical race condition
  - Writing a test that calls real ZooKeeper methods and hoping to hit the race — use mocks to deterministically trigger it
  - Forgetting that `KeeperException.NoNodeException` can also come from `getChildren` on a parent that was deleted after `getChildren` was called — test both the child-level and parent-level deletion scenarios

- **Example — Correct test approach:**
```java
// Simulate: getChildren returns a child, but the follow-up exists/getData throws NoNodeException
ZooKeeper mockZK = mock(ZooKeeper.class);
when(mockZK.getChildren(anyString(), anyBoolean(), any())).thenReturn(
    Collections.singletonList("/key_1"));
when(mockZK.exists(eq("/key_1"), anyBoolean())).thenThrow(
    new KeeperException.NoNodeException());

MyWatcher watcher = new MyWatcher(mockZK, ...);
watcher.checkForUpdates();

// Verify the watcher logged the error and continued
verify(logger).warn(contains("NoNode"));
// Verify no exception was thrown to the caller
```

- **Example — Incorrect test approach:**
```java
// BAD: Only tests the happy path, never simulates the race
ZooKeeper mockZK = mock(ZooKeeper.class);
when(mockZK.getChildren(anyString(), anyBoolean(), any())).thenReturn(
    Collections.singletonList("/key_1"));
when(mockZK.exists(eq("/key_1"), anyBoolean())).thenReturn(new Stat());

MyWatcher watcher = new MyWatcher(mockZK, ...);
watcher.checkForUpdates();
// This test passes even if the code would crash on NoNodeException
```