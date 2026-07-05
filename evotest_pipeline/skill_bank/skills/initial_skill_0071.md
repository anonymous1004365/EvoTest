---
name: permission-cache-clear-after-move
description: When testing permission enforcement during node move operations, verify
  that caches are properly invalidated. The TG should test that after a node move,
  permission checks for operations on the moved subtree (like adding properties) correctly
  enforce access rights rather than incorrectly using stale cached permissions.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# permission-cache-clear-after-move

## Instructions

# Permission Cache Clear After Move

## Instructions

- WHEN the TG encounters code that caches permission entries (e.g., `PermissionEntryCache`, `PrincipalPermissionEntries`, or any `eagerCacheSize` configuration parameter that enables caching) AND there are move-related operations (e.g., `session.move(...)`, `session.getWorkspace().move(...)`)
- THEN the TG should write a test that:
  1. Sets up a permission configuration where the eager cache size is explicitly set to a non-default value (e.g., `"eagerCacheSize", 0` to disable eager cache) OR uses a configuration that triggers the cache path
  2. Creates a source node at some path (e.g., `/test/path`), sets access control policies on it
  3. Moves the node to a new path
  4. After the move, performs an operation that modifies the moved node (e.g., adding a property like `jcr:title`)
  5. Verifies that the operation succeeds (does NOT throw `AccessDeniedException` or similar)
- The test must specifically verify that the permission check AFTER the node move correctly accounts for the new path and does NOT incorrectly apply stale cached permissions from the old path
- Common pitfalls:
  - Testing move + read operations (get properties) instead of move + write operations (add/modify properties) — the bug manifests specifically when MODIFYING the target
  - Testing move operations without also testing what happens when operations are performed on the moved node afterwards
  - Not configuring the permission cache settings (e.g., leaving `eagerCacheSize` at default instead of setting it to a value that exposes the bug)
  - Setting up permissions that are too permissive and mask the bug (e.g., test user needs read/write on both source and destination)

### Example test pattern (correct)

```java
// Set eagerCacheSize to 0 to trigger the cache path that has the bug
@Override
protected ConfigurationParameters getSecurityConfigParameters() {
    return ConfigurationParameters.of(
        AuthorizationConfiguration.NAME,
        ConfigurationParameters.of("eagerCacheSize", 0)
    );
}

@Test
public void testMoveAndAddProperty2() throws Exception {
    // Setup: create source node with specific permissions
    // Move the node to a destination
    // After move, add a property to the moved node
    // Should succeed — not throw AccessDeniedException
}
```

### Example pitfall (incorrect)

```java
// Bug: Doesn't configure eagerCacheSize — uses defaults that don't trigger the bug
@Test
public void testMoveAddProperty() throws Exception {
    // Create source node, move it
    // After move, read properties from the moved node
    // This succeeds but doesn't test the write-after-move path
    // The bug only manifests when doing WRITE operations after move
}
```