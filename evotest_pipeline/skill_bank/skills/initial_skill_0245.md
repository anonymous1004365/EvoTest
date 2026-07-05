---
name: access-control-setpolicy-writes-ac-content
description: When testing AccessControlManager.setPolicy(), verify that the policy
  content is actually persisted to the underlying JCR node (rep:policy child node
  with ACE entries). This skill catches bugs where setPolicy() succeeds without creating/storing
  the access control entries.
code_tags:
- VALIDATION
- STATE_MUTATION
- ACCESS_CONTROL_EVALUATION
test_pattern: STATE_TEST
---

# access-control-setpolicy-writes-ac-content

## Instructions

# Testing that setPolicy() Persists ACL Content

## Instructions

- WHEN the TG encounters a call to `AccessControlManager.setPolicy(String absPath, AccessControlPolicy policy)` that passes an `AccessControlList` containing entries
- THEN the TG should write a test that verifies the policy content is actually persisted and readable back, not just that `setPolicy()` returns without throwing. Call `getPolicies(absPath)` after `setPolicy()` and verify the returned policies contain the expected ACEs, principals, and privileges.

- WHEN testing `setPolicy()` with a `JackrabbitAccessControlList` that has entries added via `addAccessControlEntry(Principal principal, Privilege[] privileges)`
- THEN the TG should:
  1. Set a policy with a specific test principal (e.g., `EveryonePrincipal.getInstance()`) and specific privileges (e.g., `PrivilegeConstants.JCR_READ`)
  2. Call `getPolicies(absPath)` to retrieve the stored policy
  3. Assert the returned policy is not null, is an `AccessControlList`, and contains entries with the correct principal and privileges
  4. Use `root.hasPendingChanges()` or verify the `rep:policy` child node exists to confirm persistence
  5. If the buggy version fails to persist the content, the test should fail (e.g., `getPolicies()` returns an empty ACL or no ACL)

- Common pitfalls to avoid:
  - **Only verifying no exception is thrown**: A test that just calls `setPolicy()` and catches no exception is insufficient — the policy may not be persisted.
  - **Not calling `getPolicies()` after `setPolicy()`**: Always read back the policy to verify it was stored.
  - **Testing with a null or empty ACL**: Use a realistic `JackrabbitAccessControlList` with at least one entry containing a real principal and at least one privilege.
  - **Forgetting to refresh/commit**: Ensure the root is committed after `setPolicy()` before reading back, as some implementations may defer writes.
  - **Calling `getEffectivePolicies()` instead of `getPolicies()`**: The bug may be in the stored policy that `getPolicies()` returns, not in the effective/inherited view.

### Correct Example (pseudocode)

```java
// Setup
JackrabbitAccessControlList acl = acMgr.getApplicablePolicies(testPath).getNextAccessControlPolicy();
acl.addAccessControlEntry(EveryonePrincipal.getInstance(), privilegesFromNames(PrivilegeConstants.JCR_READ));

// Set policy
acMgr.setPolicy(testPath, acl);

// Commit and read back
root.commit();
AccessControlPolicy[] policies = acMgr.getPolicies(testPath);
assertNotNull("Expected at least one policy", policies);
assertTrue("Expected AccessControlList", policies[0] instanceof AccessControlList);
AccessControlList stored = (AccessControlList) policies[0];
assertEquals("Expected 1 ACE entry", 1, stored.getAccessControlEntries().length);
assertEquals(EveryonePrincipal.getInstance(), stored.getAccessControlEntries()[0].getPrincipal());
```

### Incorrect Example (would not catch the bug)

```java
// BAD: Only checks no exception is thrown
JackrabbitAccessControlList acl = acMgr.getApplicablePolicies(testPath).getNextAccessControlPolicy();
acl.addAccessControlEntry(EveryonePrincipal.getInstance(), privilegesFromNames(PrivilegeConstants.JCR_READ));
acMgr.setPolicy(testPath, acl);  // No exception? Test passes. But policy may not be persisted!
// Missing: read back and verify stored content
```