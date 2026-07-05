---
name: repeated-recovery-idempotency
description: When testing cluster node recovery processes that modify shared cluster
  state (like recovery locks), verify that performing recovery multiple times sequentially
  succeeds without errors and that the post-recovery state is correctly transitioned
  to "no recovery needed". This skill applies to any recovery/background process with
  mutable state and lease-based status.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# repeated-recovery-idempotency

## Instructions

# Repeated Recovery Idempotency

## Instructions

WHEN the TG encounters a method that performs recovery or cleanup operations that modify shared cluster-state documents (like `performRecoveryIfNeeded()` in `LastRevRecoveryAgent`), and the operation depends on mutable time-based conditions (e.g., lease expiry, `isRecoveryNeeded()` checks that use `clock.getTime() > nodeInfo.getLeaseEndTime()`), THEN the TG should write a test that verifies the operation can be safely called multiple times in sequence without errors.

Specifically:
- Write a test that sets up a scenario where recovery is needed (e.g., artificially advance the clock past the lease end time using `clock.waitUntil(...)`, then renew the lease for the recovering node).
- Call the recovery method (e.g., `performRecoveryIfNeeded()`) once.
- THEN assert that `isRecoveryNeeded()` returns `false` (indicating successful completion).
- THEN call the recovery method a second time and assert that it still succeeds — both the method call and the final state must be consistent.
- Use `assertFalse` to verify post-recovery state rather than just checking that no exception is thrown.

Key pitfalls to avoid:
- Do NOT only call the recovery method once — the bug manifests only on the second invocation after the first has already succeeded.
- Do NOT skip asserting `isRecoveryNeeded() == false` after the first recovery — the test must verify both that the recovery side-effect (state mutation) happened and that the method is idempotent.
- Do NOT use a single test scenario without advancing the clock — the `isRecoveryNeeded()` check depends on `clock.getTime() > leaseEndTime`, so the clock must be explicitly advanced past the lease time.

Example test pattern (correct):

```java
// 1. Create base structure that needs recovery
NodeBuilder b1 = ds1.getRoot().builder();
b1.child("x").child("y");
ds1.merge(b1, EmptyHook.INSTANCE, CommitInfo.EMPTY);
ds1.runBackgroundOperations();
ds2.runBackgroundOperations();

// 2. Have C2 make changes that need recovery
NodeBuilder b2 = ds2.getRoot().builder();
b2.child("x").child("y").child("z").setProperty("foo", "bar");
ds2.merge(b2, EmptyHook.INSTANCE, CommitInfo.EMPTY);

// 3. Wait for lease to expire for C1, then renew C1's lease
long leaseTime = ds1.getClusterInfo().getLeaseTime();
ds1.runBackgroundOperations();
clock.waitUntil(clock.getTime() + leaseTime + 10);
ds1.getClusterInfo().renewLease();

// 4. Assert recovery is needed
assertTrue(ds1.getLastRevRecoveryAgent().isRecoveryNeeded());

// 5. Perform recovery (first call - should succeed)
ds1.getLastRevRecoveryAgent().performRecoveryIfNeeded();

// 6. Assert recovery is no longer needed after first invocation
assertFalse(ds1.getLastRevRecoveryAgent().isRecoveryNeeded());

// 7. Perform recovery AGAIN (second call - this is the key test)
ds1.getLastRevRecoveryAgent().performRecoveryIfNeeded();

// 8. Assert recovery is still not needed after second invocation
assertFalse(ds1.getLastRevRecoveryAgent().isRecoveryNeeded());
```

Incorrect approach (common pitfall):

```java
// WRONG: Only calls recovery once and doesn't assert post-recovery state
ds1.getLastRevRecoveryAgent().performRecoveryIfNeeded();
// No second call, no state assertion - won't catch the bug!

// WRONG: Calls recovery twice without verifying first recovery's side effects
ds1.getLastRevRecoveryAgent().performRecoveryIfNeeded();
ds1.getLastRevRecoveryAgent().performRecoveryIfNeeded(); // may throw on buggy version
// Missing assertFalse(isRecoveryNeeded()) after first call - can mask the bug
```