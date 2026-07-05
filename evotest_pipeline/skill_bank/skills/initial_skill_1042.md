---
name: version-history-copy-validation
description: WHEN the TG encounters code that copies version history between JCR repositories
  (e.g., during upgrade or sidegrade), THEN it should test that version history nodes
  can close properly and release locks after the copy operation completes. This skill
  catches cases where versionable nodes fail to close their sessions, leading to "Failed
  to copy content" errors.
code_tags:
- NULL_CHECK
- RESOURCE_MANAGEMENT
test_pattern: STUB_TEST
---

# version-history-copy-validation

## Instructions

# Version History Copy Validation

## Instructions

- WHEN the TG encounters code that copies version history between JCR repositories (e.g., `RepositoryUpgrade.copy()` or `RepositorySidegrade.copy()` in Apache Jackrabbit Oak)
  - THEN it should write a test that:
    1. Sets up a source repository with at least one versioned node (e.g., using `JcrUtils.getOrCreateByPath("/test", ...)` and `session.getWorkspace().getVersionManager().checkin("/test")`)
    2. Configures `CopyVersionHistory` to `true` in the upgrade configuration
    3. Sets `onlyReferenced` to `true` to filter which versions are copied
    4. Creates a node with a `mix:versionable` mixin and adds a property (e.g., `jcr:versionLabel`) to influence version reference traversal
    5. Calls the copy/upgrade method and expects no `RepositoryException` with message "Failed to copy content"
    6. Verifies that version histories are accessible on the target repository after the copy (e.g., by calling `getVersionHistory` on the copied node)
  - The test should verify that when version history nodes contain references to versionable nodes that are still open/active, those references are properly resolved and the sessions/resources are closed, rather than causing a "Failed to copy content" exception.
  - Common mistakes to avoid:
    - Testing only unversioned content (the bug specifically involves versionable nodes)
    - Testing only without the `onlyReferenced` flag (the bug manifests when version references are filtered)
    - Using mock repositories instead of real ones (the bug involves actual session/resource lifecycle)
    - Forgetting to close sessions in tear-down (which can mask resource leaks or create flaky tests)
    - Testing only a single versioned node (the bug involves multiple versions with different states — checked-in, checked-out, labeled)

### Correct Test Pattern (conceptual)
```java
@Test
public void testVersionHistoryCopyWithVersionableReferences() throws Exception {
    // Setup source repository
    Session sourceSession = createSourceRepository();
    Node versionableNode = sourceSession.getRootNode().addNode("testNode", "nt:unstructured");
    versionableNode.addMixin("mix:versionable");
    sourceSession.save();
    
    // Create multiple versions
    VersionManager vm = sourceSession.getWorkspace().getVersionManager();
    vm.checkin("/testNode");
    vm.checkout("/testNode");
    versionableNode.setProperty("jcr:versionLabel", "v1.0");
    sourceSession.save();
    
    // Setup target repository
    Session targetSession = createTargetRepository();
    
    // Configure copy with onlyReferenced = true
    UpgradeConfiguration config = new UpgradeConfiguration();
    config.setCopyVersionHistory(true);
    config.setVersionCopyConfiguration(...);
    
    // Execute copy - should NOT throw RepositoryException
    RepositoryUpgrade upgrade = new RepositoryUpgrade(sourceRepository, targetRepository, config);
    upgrade.copy();
    
    // Verify version history was copied
    Node copiedNode = targetSession.getRootNode().getNode("testNode");
    VersionHistory vh = targetSession.getWorkspace().getVersionManager().getVersionHistory(copiedNode.getPath());
    assertNotNull(vh);
}
```

### Incorrect Test Pattern (common pitfalls)
```java
// BAD: Only tests unversioned content - won't catch versionable node reference issues
@Test
public void testCopyWithoutVersioning() throws Exception {
    // ... no versionable mixin, no checkin/checkout, no version labels
    RepositoryUpgrade upgrade = new RepositoryUpgrade(source, target, config);
    upgrade.copy(); // passes on buggy code, but misses the bug entirely
}
```