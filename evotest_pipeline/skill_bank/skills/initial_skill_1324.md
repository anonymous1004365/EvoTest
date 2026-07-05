---
name: standby-failover-empty-state-detection
description: When testing standby failover synchronization between a primary and a
  standby Oak segment store, the TG should verify that after failover the standby
  store contains the expected replicated content (not an empty/uninitialized root
  state). This skill helps detect cases where the standby fails to properly sync data
  from the primary.
code_tags:
- STANDBY_SYNC_FAILOVER
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# standby-failover-empty-state-detection

## Instructions

# Standby Failover Empty State Detection

## Instructions

- WHEN the TG is testing a standby failover scenario where content is written to a primary (server) store and then a standby (client) store synchronizes from it
- THEN the TG should verify that after the synchronization and failover, the standby store's root node contains the expected content (e.g., child nodes, properties) rather than an empty `{ root : { } }` state
- The test should:
  1. Write content (e.g., child nodes, properties) to the primary/server store
  2. Trigger synchronization from the standby/client to the primary
  3. Wait for the synchronization to complete (use appropriate polling/sleep)
  4. After failover (stop the primary, use the standby), verify the standby store's session/node contains the expected content, e.g., `assertNotNull(session.getNode("/expectedNode"))` or compare the root node state
- Expect that on the buggy version, the standby store will contain an empty root (`{ root : { } }`) instead of the replicated content (`{ root = { ... } }`), causing the assertion to fail with a message like `expected:<{ root = { ... } }> but was:<{ root : { } }>`
- Common pitfalls to avoid:
  - **Starting the standby before the primary**: The order of server/client initialization matters — ensure the primary (server) is started and content is written before the standby (client) connects and syncs
  - **Not waiting for sync to complete**: The synchronization is asynchronous; the test must wait (e.g., `Thread.sleep` with sufficient duration) before asserting content on the standby
  - **Testing only the primary store**: The assertion must be made against the **standby** store/session, not the primary, to verify replication actually occurred
  - **Using only one session**: Multiple sessions may be needed — one for writing to the primary and one for reading from the standby

### Correct Example (pseudo-code)
```java
// Start primary server
StandbyServerSync server = new StandbyServerSync(...);
server.start();

// Write content to primary store
Session primarySession = repository.login(credentials);
primarySession.getNode("/").addNode("testNode");
primarySession.save();

// Start standby client and sync
StandbyClientSync client = new StandbyClientSync(...);
client.start();
Thread.sleep(5000); // wait for sync to complete

// After failover, check standby has the content
Session standbySession = standbyRepo.login(credentials);
assertNotNull("Standby should have replicated node", standbySession.getNode("/testNode"));
assertNotEquals("Standby should not be empty", "{ root : { } }", getRootState(standbySession));
```

### Incorrect Example (pitfall)
```java
// BAD: Starting client before server/primary
StandbyClientSync client = new StandbyClientSync(...);
client.start();

StandbyServerSync server = new StandbyServerSync(...);
server.start();

// Write content after both started
Session session = repository.login(credentials);
session.getNode("/").addNode("testNode");
session.save();
// BAD: no wait for sync
// BAD: asserting on primary session, not standby
assertNotNull("This checks primary, not standby", session.getNode("/testNode"));
```