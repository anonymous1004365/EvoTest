---
name: failover-mongodb-replica-set-sync-behavior
description: WHEN testing MongoDB failover scenarios with replica sets, THEN the test
  must verify that node synchronization works correctly across the full session lifecycle
  — creation, replication, deletion, and re-creation — not just reading after a single
  write. The TG should test concurrent session synchronization under failover conditions
  by adding followed by removing and re-adding the same node, verifying state convergence
  after each mutation.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# failover-mongodb-replica-set-sync-behavior

## Instructions

# MongoDB Replica Set Failover Synchronization Test

## Instructions

- WHEN testing node synchronization across MongoDB replica set members (e.g., `s1` and `s2` connecting to `mongodb://localhost:27017,localhost:27018,localhost:27019/oak`)
- THEN the test must verify that state mutations (add, remove, re-add of the same node) are correctly synchronized between sessions after each mutation, not just after a single add
- Specifically, the test should:
  1. Add a node to session `s1` and save
  2. Refresh session `s2` and verify the node appears (with a retry loop up to 5 seconds for eventual consistency)
  3. Remove the node from `s2` and save
  4. Refresh session `s1` and verify the node is removed (with retry loop up to 5 seconds)
  5. Re-add the same node to `s1` and save
  6. Refresh session `s2` and verify the node re-appears (with retry loop up to 5 seconds)
  7. Remove the node from `s2` and save again
- Each verification step should use `s2.refresh(false)` to force a refresh (not auto-refresh), then check `s2.getRootNode().hasNode(nodeName)`, looping through `seconds(5)` with `Thread.sleep(1000)` for up to 5 retries
- The test should accept eventual consistency by using retry loops rather than immediate assertions
- Common pitfalls to avoid:
  - Testing only a single write operation followed by a read — this misses the critical failover behavior where node removal and re-creation stress the replica set synchronization
  - Using auto-refresh or relying on default refresh behavior — must explicitly call `s2.refresh(false)` and `s1.refresh(false)`
  - Not retrying the assertion in a loop — immediate assertion may fail due to replica set lag
  - Not using `@Ignore("OAK-759")` annotation — this test is known to be flaky and should be ignored in normal CI runs

### Example: Correct test pattern
```java
@Override
protected NodeStoreFixture getFixture() {
    return new DocumentMongoFixture(
            "mongodb://localhost:27017,localhost:27018,localhost:27019/oak", null);
}

@Test
public void test() throws Exception {
    if (s1 == null) return;
    if (s1.getRootNode().hasNode("test")) {
        s1.getRootNode().getNode("test").remove();
    }
    for (int i = 0; i < 100; i++) {
        String nodeName = "test" + i;
        s1.getRootNode().addNode(nodeName);
        s1.save();
        for (int x : seconds(5)) {
            s2.refresh(false);
            if (s2.getRootNode().hasNode(nodeName)) break;
        }
        s2.getRootNode().getNode(nodeName).remove();
        s2.save();
        for (int x : seconds(5)) {
            s1.refresh(false);
            if (!s1.getRootNode().hasNode(nodeName)) break;
        }
        s1.getRootNode().addNode(nodeName);
        s1.save();
        for (int x : seconds(5)) {
            s2.refresh(false);
            if (s2.getRootNode().hasNode(nodeName)) break;
        }
        s2.getRootNode().getNode(nodeName).remove();
        s2.save();
    }
}
```

### Incorrect pattern (missing remove/re-add cycle):
```java
// WRONG: only tests add once, does not test remove + re-add
s1.getRootNode().addNode("test0");
s1.save();
s2.refresh(false);
assertTrue(s2.getRootNode().hasNode("test0")); // immediate assertion, no retry loop
```