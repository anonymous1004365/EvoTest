---
name: permission-aware-gettree-testing
description: WHEN testing Root.getTree() for paths where intermediate nodes are absent,
  THEN verify that a non-null Tree is returned for the target path while respecting
  access control permissions on the parent nodes.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# permission-aware-gettree-testing

## Instructions

# Testing Permission-Aware getTree() with Missing Intermediate Nodes

## Instructions

WHEN the TG encounters a `Root.getTree(String path)` implementation that checks access control permissions on parent nodes (e.g., via `TreePermission` or `PermissionProvider`) and the method should return a non-null `Tree` for a valid child path even when the intermediate parent node is not visible/accessible to the current session:

- THEN the TG should write a test that:
    1. Creates a tree structure where a child node exists at a path (e.g., `/a/b/c`) but the intermediate parent (e.g., `/a/b`) does NOT have read permission for the session.
    2. Calls `root.getTree("/a/b/c")` on a session that does NOT have access to `/a/b`.
    3. Asserts that the returned `Tree` is non-null and its path is `/a/b/c`.
    4. Also asserts that `root.getTree("/a/b")` returns a non-null `Tree` (since some implementations return a non-accessible tree wrapper rather than null) or verifies the specific behavior of the session for the intermediate path.

- WHEN writing the setup for such a test:
    - THEN ensure the session has access to the leaf node but NOT to the intermediate parent.
    - THEN verify that the session's permission evaluation does not throw `AccessDeniedException` during `getTree()` but correctly evaluates permissions through `TreePermission` chain.

- Common pitfalls to avoid:
    - Testing only paths where ALL ancestors are visible — the bug manifests specifically when an intermediate node is invisible.
    - Assuming `getTree()` returns `null` for inaccessible paths — the buggy implementation may return a non-null but broken `Tree` that has wrong path or throws on subsequent operations.
    - Using `root.getTree("/")` as the base and checking children individually — the test must go through a specific path where an intermediate node is missing/not-accessible.
    - Testing the authorization Root directly without setting up proper access control entries (ACEs) on the intermediate nodes.

- Correct test pattern (Java/JUnit):
```java
// Setup: Create ACEs so that "/a" is readable, "/a/b" is not readable, but "/a/b/c" is readable
// Then:
Tree t = root.getTree("/a/b/c");
assertNotNull("getTree should return non-null for accessible child even when parent is not accessible", t);
assertEquals("/a/b/c", t.getPath());
```

- Incorrect test pattern (would NOT catch the bug):
```java
// Only testing with fully accessible paths:
Tree t = root.getTree("/a/b/c");
assertTrue(t.exists());
// This misses the bug because intermediate nodes are all visible
```