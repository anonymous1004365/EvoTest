---
name: cluster-id-initialization-state-mutation
description: Detects bugs where an internal cluster ID is lazily initialized but not
  persisted back to a shared mutable state holder, causing stale reads. When a method
  reads a mutable field, computes a derived value (e.g., cluster ID), and returns
  it without updating the field, other callers may see an empty/uninitialized value.
  Apply this skill when you see get-or-create logic on atomic/mutable fields that
  is not idempotent.
code_tags:
- CLUSTERED_OPERATIONS
- CLUSTER_ID_INITIALIZATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# cluster-id-initialization-state-mutation

## Instructions

# Cluster ID Initialization — Mutable State Missed Write-Back

## Instructions

**WHEN** the TG encounters a class that has a `volatile` or mutable field (e.g., `AtomicReference`, `volatile Set<Integer>`, `Map`) intended to hold a computed/cluster-related value that is lazily initialized:

- **THEN** the TG should inspect all methods that **read** that field and return a derived **or** related value (e.g., a new `Set<Integer>` built from the field's current contents). If the method **computes a new collection/object** from the field's current value but **never writes the result back** into the field, the method is buggy:  
  - On first call, the field is `null`/empty → a default empty collection is returned.  
  - On a subsequent call after a side-effect has populated the field, the field *now* contains data, but the method returns a stale reference or empty copy from the earlier initialization path.  
  - The fix must ensure that the *first-time computation* and every subsequent computation **always** stores the derived value back into the mutable field.

- **THEN** the TG should write a test that exercises the *first call* (when the field is still `null`/empty), performs a side-effect mutation (e.g., adding an element to the mutable field via a separate public method), and then calls the lazy-getter method again. The test must **assert** that the second call returns a non-empty collection reflecting the side-effect, **not** an empty one.

- **Include concrete examples**:  
  If the field is `private volatile Set<Integer> inactiveClusterIds = null;` and the method `getInactiveClusterIds()` does:
  ```java
  if (inactiveClusterIds == null) {
      return Collections.emptySet();
  }
  return inactiveClusterIds;
  ```
  then after calling `addInactiveClusterId(42)`, the field is `{42}` but `getInactiveClusterIds()` still returns `Collections.emptySet()` because the null-check returns early. The fix must be:
  ```java
  if (inactiveClusterIds == null) {
      inactiveClusterIds = new HashSet<>();
  }
  return inactiveClusterIds;
  ```

- **Common pitfall**: Testing only the *post-mutation* scenario (e.g., calling `addInactiveClusterId` before `getInactiveClusterIds`) without testing the *empty-before-mutation → mutate → read-after-mutation* sequence. This will miss the bug because the null-init path only triggers on the very first access.

## Example Test

```java
// Correct test that catches the bug:
@Test
public void testInactiveClusterIdsAfterMutation() {
    // 1. First call on empty state — buggy version returns empty set
    // 2. Add a cluster ID via the mutator
    // 3. Second call should now include the added ID, but buggy version
    //    still returns the empty set from step 1 (or an empty set)
    DocumentNodeStore store = ...;
    Set<Integer> before = store.getInactiveClusterIds(); // returns empty set (correct so far)
    store.addInactiveClusterId(42);                       // mutates internal state
    Set<Integer> after = store.getInactiveClusterIds();   // BUG: still empty!
    assertFalse("inactive cluster IDs should contain 42 after add", after.isEmpty());
    assertTrue(after.contains(42));
}
```

## Incorrect Test (does NOT catch the bug)

```java
// This test would PASS on the buggy version, masking the bug:
@Test
public void testInactiveClusterIdsDirect() {
    DocumentNodeStore store = ...;
    store.addInactiveClusterId(42);
    // This triggers the same null-path because the field was never
    // written back — but the test doesn't verify post-mutation reading
    Set<Integer> ids = store.getInactiveClusterIds();
    // Buggy: still empty, but test assumes it's non-empty — FAILS but
    // doesn't isolate the root cause. Worse, if the test checks for
    // empty, it would pass on the bug.
    assertTrue(ids.isEmpty()); // passes on buggy version, wrong!
}
```