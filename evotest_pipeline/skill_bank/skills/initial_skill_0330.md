---
name: traversal-ordering-during-node-state-copy
description: When using a NodeStateCopier with include/exclude path filters, the order
  of traversal must be considered because mutable state mutations from one traversal
  can affect the correctness of subtrees visited later. Write tests that validate
  complete content after copying, not just existence of specific nodes.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
- ORDER_DEPENDENCY
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# traversal-ordering-during-node-state-copy

## Instructions

# Traversal Ordering During Node State Copy

## Instructions

- WHEN the TG encounters code that copies content between node states or repositories using `NodeStateCopier.builder()` with include paths (e.g., `includePaths(paths)`), exclude paths, and/or merge paths
- THEN the TG should write a test that:
  1. Creates a source NodeState with a tree structure containing content under multiple sub-paths (e.g., several version history nodes under `/jcr:system/jcr:versionStorage/`)
  2. Copies the content using `NodeStateCopier.builder()` with specific include and exclude paths, and tests the resulting target NodeState
  3. **Verifies ALL expected content exists in the target** after the copy, not just that a specific path was copied — traverse the full target tree and validate the complete structure
  4. When paths include version-related content (e.g., `/jcr:system/jcr:versionStorage` with merged subtrees), ensure that the copy correctly handles traversal of sibling subtrees when nodes at a merged path may be modified during the copy
  5. Expect the buggy version to fail with "Failed to copy content" exception wrapping a `NullPointerException` or `CommitFailedException` when copying certain subtrees
- Common pitfalls:
  - Testing only that a single path was copied, without validating that all sibling subtrees were also copied correctly
  - Not testing with versionable content that has multiple version histories under the version storage tree
  - Assuming that because a node exists in the source, it will exist in the target after copying with merge paths — the order of traversal can cause nodes modified during the copy to affect sibling traversal

### Correct example (catches the bug):
```java
// Test that verifies complete structure after copying with version storage
// Setup source with multiple version histories under jcr:versionStorage
NodeState source = createSourceWithMultipleVersions();
NodeStateBuilder targetBuilder = ...;

NodeStateCopier.builder()
    .includePaths(Set.of("/jcr:system/jcr:versionStorage"))
    .mergePaths(Set.of("/jcr:system/jcr:versionStorage"))
    .build()
    .copy(source, targetBuilder.getNodeState());

NodeState target = targetBuilder.getNodeState();
// Verify ALL version histories were copied, not just one
assertTrue(target.exists());
assertTrue(target.getChildNode("jcr:system").getChildNode("jcr:versionStorage").exists());
int childCount = countChildren(target.getChildNode("jcr:system").getChildNode("jcr:versionStorage"));
assertEquals("Expected all version histories to be copied", expectedCount, childCount);
```

### Incorrect example (misses the bug):
```java
// Only checks that copy doesn't throw — does NOT validate content
NodeStateCopier.builder()
    .includePaths(Set.of("/jcr:system/jcr:versionStorage"))
    .mergePaths(Set.of("/jcr:system/jcr:versionStorage"))
    .build()
    .copy(source, target);

// Missing: no assertion that all expected content exists in target
```