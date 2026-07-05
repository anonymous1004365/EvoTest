---
name: version-history-format-validation
description: When copying version histories during repository upgrade, child node
  names that are not valid version UUIDs should not be added to the version history
  set. This skill teaches how to validate that only correct UUID-format version child
  nodes are included in the copied version history.
code_tags:
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# version-history-format-validation

## Instructions

# Version History Child Node Format Validation

## Instructions

- WHEN the TG encounters code that copies version histories from a source repository to a target repository, where version histories may contain child nodes with names that could be either UUIDs (representing actual versions) or non-UUID names (representing child nodes of the versionable node, like "jcr:childVersionHistory")
- THEN the TG should write a state verification test that:
  1. Creates a source repository with a versionable node
  2. Adds a child node under the versionable node (e.g., named "child" or any non-UUID name)
  3. Saves and versions the parent node, creating a version history
  4. Upgrades/copies the version history to a target repository
  5. Asserts that the target repository's version history set contains ONLY UUID-format entries for actual versions, NOT the names of child nodes that were added under the versionable node
  6. Expects that on the buggy version, the child node name (e.g., "child" or "ffec28b7-3e34-428e-8b30-6aea10b2a989/child") incorrectly appears in the version history set, while on the fixed version, only the actual version UUID appears

- Example test pattern:
```java
// CORRECT: Verify version history contains only UUID-format child names
@Test
public void testVersionHistoryExcludesNonVersionChildNodes() throws Exception {
    // Setup source repository
    Node rootNode = getNode("/content");
    Node versionableNode = rootNode.addNode("versionableNode");
    versionableNode.addMixin("mix:versionable");
    
    // Add a child node that is NOT a version
    Node childNode = versionableNode.addNode("child", "nt:unstructured");
    childNode.setProperty("prop", "value");
    
    // Save and checkout/checkin to create versions
    session.save();
    session.getWorkspace().getVersionManager().checkin("/content/versionableNode");
    
    // Perform upgrade/copy
    upgradeRepository(sourceRepo, targetRepo);
    
    // Verify version history in target contains only UUID-format entries
    VersionHistory versionHistory = targetSession.getWorkspace()
        .getVersionManager().getVersionHistory("/content/versionableNode");
    
    // Version history should NOT include child node name
    assertFalse("Child node name should not appear in version history",
        containsItem(versionHistory, "child"));
    
    // But should include the version UUID
    assertTrue("Version UUID should appear in version history",
        containsItem(versionHistory, "e029df41-62f5-4ab8-9251-3288131460ce"));
}
```

```java
// INCORRECT: Only tests with basic versionable nodes, no child nodes under them
@Test
public void testVersionHistoryWithNoChildNodes() throws Exception {
    // Only creates a simple versionable node with no child content
    // This would NOT catch the bug because the bug only manifests when
    // child nodes exist under the versionable node at version creation time
    Node versionableNode = rootNode.addNode("versionableNode");
    versionableNode.addMixin("mix:versionable");
    session.save();
    session.getWorkspace().getVersionManager().checkin("/content/versionableNode");
    // ... assert version history exists but never tests with child nodes
}
```

- Common pitfalls to avoid:
  - Testing version history with only the versionable node itself (no child nodes) — this won't trigger the bug
  - Only verifying that version UUIDs exist in the history without checking that non-UUID child names are absent
  - Assuming that `getNodes()` on a VersionHistory only returns version nodes and not child nodes from the versionable node's content
  - Using `contains()` on version history entries without checking the actual names (UUID format vs plain names)