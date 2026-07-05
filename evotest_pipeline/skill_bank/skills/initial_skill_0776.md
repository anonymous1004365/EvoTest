---
name: version-storage-getchildrencount-access
description: When a test calls Tree.getChildrenCount() on a version storage node accessed
  through a restricted session, it may fail due to unhandled access control evaluation.
  Use this skill to ensure proper permission setup before invoking getChildrenCount
  on version storage paths.
code_tags:
- ACCESS_CONTROL_EVALUATION
test_pattern: INTERACTION_TEST
---

# version-storage-getchildrencount-access

## Instructions

# Version Storage getChildrenCount Access Control Test

## Instructions

- WHEN the TG encounters code that calls `Tree.getChildrenCount(long)` on a node inside the JCR version storage (path starts with `VersionConstants.VERSION_STORE_PATH` e.g. `"/jcr:system/jcr:versionStorage"`) using a restricted (non-admin) session obtained via `getTestRoot()` or similar
- THEN the TG should write a test that:
  1. First grants `PrivilegeConstants.JCR_READ` privilege to the test principal at the root path `"/"` using `setupPermission("/", testPrincipal, true, PrivilegeConstants.JCR_READ)` BEFORE accessing the version storage
  2. Then obtains a test root via `getTestRoot()`, retrieves the version storage tree at `VersionConstants.VERSION_STORE_PATH`, and calls `vs.getChildrenCount(Long.MAX_VALUE)`
  3. Verifies that the method executes without throwing any exception (no assertion on the return value is needed — the call itself is the validation that access control does not crash)
- The bug occurs because `PermissionStoreImpl.getNumEntries()` calls `tree.getChildrenCount(max)` on the principal root tree, and when invoked with a restricted session, the underlying access control evaluation on version storage paths throws an exception. The fix ensures access is properly checked or the principal tree exists with appropriate permissions.
- Common pitfalls to avoid:
  - Do NOT test `getChildrenCount` on the version storage without first granting read permissions — the test will fail with an access denied exception on the buggy version
  - Do NOT use `root` (the admin session's root) instead of `getTestRoot()` (the restricted session's root) — the bug is specifically about access control evaluation on a restricted session
  - Do NOT use `assertNotNull` or other assertions on the result — the test should simply invoke `getChildrenCount` and let any exception propagate (the test method signature should declare `throws Exception`)
  - Do NOT test with `getChildrenCount(0)` — the bug manifests specifically when called with `Long.MAX_VALUE` as the max parameter

### Correct Example

```java
@Test
public void testGetChildrenCountOnVersionStorage() throws Exception {
    setupPermission("/", testPrincipal, true, PrivilegeConstants.JCR_READ);
    Tree vs = getTestRoot().getTree(VersionConstants.VERSION_STORE_PATH);
    vs.getChildrenCount(Long.MAX_VALUE);
}
```

### Incorrect Examples

```java
// WRONG: No read permission granted — will fail on buggy version
@Test
public void testGetChildrenCountOnVersionStorage() throws Exception {
    Tree vs = getTestRoot().getTree(VersionConstants.VERSION_STORE_PATH);
    vs.getChildrenCount(Long.MAX_VALUE);  // throws AccessDeniedException
}

// WRONG: Using admin session instead of restricted test session
@Test
public void testGetChildrenCountOnVersionStorage() throws Exception {
    setupPermission("/", testPrincipal, true, PrivilegeConstants.JCR_READ);
    Tree vs = root.getTree(VersionConstants.VERSION_STORE_PATH);  // admin, not restricted
    vs.getChildrenCount(Long.MAX_VALUE);  // won't trigger the bug
}
```