---
name: relative-path-addnode-authorization
description: WHEN testing node addition with relative paths (e.g., "../child") under
  authorization constraints, THEN verify that the permission check correctly resolves
  and validates the relative path against the repository root to avoid false access
  denied or false access granted. This skill applies to any JCR implementation where
  addNode() or similar mutation accepts relative paths and must verify permissions
  on the resolved absolute path.
code_tags:
- PATH_PARSING_VALIDATION
- VALIDATION
- CONSTRAINT_VIOLATION_TYPE
test_pattern: EXCEPTION_TEST
---

# relative-path-addnode-authorization

## Instructions

# Relative Path Authorization in addNode()

## Instructions

WHEN the TG encounters code where `javax.jcr.Node.addNode(String relPath)` or `javax.jcr.Node.addNode(String relPath, String primaryNodeTypeName)` is called with a relative path (e.g., `"../child"`, `"../../sibling"`, `"subdir/../child"`) in a security-sensitive context, AND the repository has authorization/permission checks that resolve the target path before verifying access:

- THEN the TG should write a test that:
  1. Sets up a controlled authorization environment where the test user has permission on the current node but NOT on the node targeted by the relative path (e.g., the parent or a sibling)
  2. Calls `addNode(...)` with a relative path that resolves outside the accessible scope (e.g., `superuserSession.getNode("/path").addNode("../restrictedChild")` where the user has no write access to the resolved path `/restrictedChild`)
  3. Expects the call to throw `javax.jcr.AccessDeniedException` (or `org.apache.jackrabbit.oak.api.security.authorization.AccessControlConstants` equivalent) because the resolved target path should fail the authorization check
  4. Verifies that the relative path is correctly resolved to an absolute path **before** the permission check, not after

- The TG should include concrete assertions:
  - `assertThrows(AccessDeniedException.class, () -> { testSession.getNode("/accessible/path").addNode("../restrictedChild"); });`
  - The test must fail on the buggy version (where relative paths bypass authorization) and pass on the fixed version

- Common pitfalls to avoid:
  - ❌ Testing only with absolute paths (these already work correctly and don't catch the bug)
  - ❌ Testing only with relative paths that stay within the accessible subtree (e.g., `"child"` or `"child/grandchild"`) — these never trigger the bug because the resolved path is still authorized
  - ❌ Testing with a superuser/admin session — the bug only manifests when the session has restricted permissions
  - ❌ Assuming the test should verify success — this bug causes incorrect **allowance**, so the test must verify **denial** (expect an exception)
  - ❌ Forgetting to verify the exception type — catching a generic `RepositoryException` may hide the specific `AccessDeniedException` that the fix introduces

### Correct Example (would catch this bug):

```java
// Setup: testUser has jcr:addChildNodes on /test but NOT on /
@Test
public void testAddNodeWithRelativePath() throws Exception {
    // Given: testUser has ALL permissions on /test subtree
    // And: testUser has NO permissions on /restricted area
    
    Node accessibleNode = testSession.getNode("/test");
    
    // When: adding a node with relative path ".." escaping the allowed scope
    assertThrows(AccessDeniedException.class, () -> {
        accessibleNode.addNode("../restrictedChild");
    });
    
    // Then: AccessDeniedException is thrown because the resolved path
    // /restrictedChild is not in the user's authorized scope
}
```

### Incorrect Example (would miss this bug):

```java
// ❌ This only tests an absolute path — no relative path resolution issue
@Test 
public void testAddNodeAbsolutePath() throws Exception {
    assertThrows(AccessDeniedException.class, () -> {
        testSession.getRootNode().addNode("/test/child");
    });
}
```

```java
// ❌ This uses a superuser — never triggers authorization at all
@Test
public void testAddNodeWithSuperuser() throws Exception {
    Node n = superuserSession.getNode("/test").addNode("../child");
    assertNotNull(n); // Always passes because superuser ignores permissions
}
```

### Key insight:
The bug occurs when the permission validator resolves the target path for `addNode()` without properly accounting for ".." segments in relative paths. The authorization check sees the parent path (which IS authorized) instead of the resolved child path. The test must use a relative path like `"../x"` that resolves to a location OUTSIDE the user's authorized scope to expose this discrepancy.