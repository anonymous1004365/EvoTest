---
name: access-control-restriction-under-test
description: When testing permission evaluation that involves access control restrictions
  on paths, the TG should include at least one child node that is deeper than the
  restricted path to verify that restrictions are properly inherited and evaluated
  for all descendant nodes.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ACCESS_CONTROL_EVALUATION
test_pattern: STATE_TEST
---

# access-control-restriction-under-test

## Instructions

# Access Control Restriction Under Test

## Instructions

- WHEN the TG encounters code that evaluates user permissions (e.g., `isGranted`, `hasPermission`, `PermissionProvider`) where access control restrictions (like path restrictions, glob patterns, or node type restrictions) are involved
- THEN the TG should **include test cases where the evaluated path is a descendant (child or grandchild) of the restricted path, not just the exact restricted path itself**. For example, if the restriction is applied to `/testRoot/a/b`, the test should check permissions on `/testRoot/a/b/c` (a child node), not just on `/testRoot/a/b`.
- The test should set up a permission entry with a particular restriction (e.g., a path restriction `PATH_RESTRICTION` to `/testRoot/a/b`), grant a specific permission (e.g., `Permissions.REMOVE_NODE` = 64) on that path, then verify that a **different user** (one who has no granted permissions) does **NOT** have that permission on a descendant path.
- Use a repository setup that creates the `testRoot`, grants `jcr:all` to an admin user first, then creates a specific permission entry with restrictions for a test user, and then verifies the test user's permissions on descendant paths.
- Common pitfalls to avoid:
  - Only testing the exact path where the restriction is applied (e.g., only `/testRoot/a/b`) without testing deeper child paths (e.g., `/testRoot/a/b/c`), which may mask bugs where restrictions are not properly enforced on descendants.
  - Not setting up the full parent-child path hierarchy under the restricted path before evaluating permissions.
  - Forgetting to differentiate between admin setup permissions and test user permissions when verifying results.
  - Using `assertTrue` when the test expects `false` (permission denied) on the descendant path.

### Correct Example

```java
// Setup admin content
adminSession.getRootNode().addNode("testRoot").addNode("a").addNode("b").addNode("c");

// Grant jcr:all to admin on testRoot
// Create a permission entry for testUser with PATH_RESTRICTION to /testRoot/a/b
// Grant REMOVE_NODE permission on /testRoot/a/b for testUser

// Test: user should NOT have REMOVE_NODE on descendant path
assertFalse("user should not have 64 on /testRoot/a/b/c",
    testSession.hasPermission("/testRoot/a/b/c", 64));
```

### Incorrect Example (bug-prone)

```java
// Only tests the exact restricted path, missing the child path bug
assertFalse("user should not have 64 on /testRoot/a/b",
    testSession.hasPermission("/testRoot/a/b", 64));
// Missing test for /testRoot/a/b/c - this is where the bug manifests
```