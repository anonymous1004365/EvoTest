---
name: orphaned-versions-copy-configuration-validation
description: When testing version history copy with orphaned versions configuration,
  verify that mix:simpleVersionable nodes missing jcr:versionHistory are properly
  skipped or handled. Use CopyVersionHistoryTest patterns where setup() configures
  VersionCopyConfiguration to copy orphaned versions within specific date ranges.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_TRANSITION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# orphaned-versions-copy-configuration-validation

## Instructions

# Orphaned Versions Copy Configuration Validation

## Instructions

- WHEN the TG encounters a test that configures `VersionCopyConfiguration` with `setCopyOrphanedVersions()` using a `Predicate<Version>` or `null`, and the test scenario involves a mix:simpleVersionable node whose `jcr:versionHistory` references a version that existed before the versionable node's creation
- THEN the TG should verify that:
  1. The test creates exactly one version for the versionable node (via `session.save()` or version manager)
  2. The test configures `config.setCopyOrphanedVersions(...)` with a `Predicate<Version>` that restricts the date range (e.g., `betweenHistories` rather than copying all old versions)
  3. The test checks that the versionable node's `jcr:versionHistory` property exists and is properly set after the copy operation
  4. A node like `mix:simpleVersionable/old` that existed before the versionable node's creation should NOT have its `jcr:versionHistory` property set, because the referenced version history was never copied (it was filtered out by the orphaned versions predicate)

- Common pitfalls to avoid:
  - **Testing only the happy path**: Do NOT assume that version history nodes exist for all versionable nodes; test the case where a versionable node references a version history that was excluded from the copy
  - **Scoping too broadly**: The bug is specifically about nodes with `mix:simpleVersionable` (not `mix:versionable`) where the `jcr:versionHistory` property references a version history node that falls outside the orphaned versions copy predicate's date range
  - **Forgetting to assert absence**: After the copy operation, verify that `mix:simpleVersionable/old` does NOT have `jcr:versionHistory` set (it was an orphaned version that failed to copy)
  - **Incorrect predicate logic**: The `Predicate<Version>` passed to `setCopyOrphanedVersions()` must filter by version date, and the date range must exclude the old version but include the current one

- Example correct approach:
  ```java
  // Setup: create versionable node, save, then create second version with delay
  // Configure: copy orphaned versions only between the two version dates
  config.setCopyOrphanedVersions(betweenHistories);
  
  // After copy: verify the old node's jcr:versionHistory is NOT present
  // because its referenced version was outside the predicate
  ```

- Example incorrect approach:
  ```java
  // WRONG: This doesn't test the edge case of version outside predicate
  // Either copies nothing or copies everything, missing the filtering logic
  config.setCopyOrphanedVersions(null); // copies all orphaned versions
  ```