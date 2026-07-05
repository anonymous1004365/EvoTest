---
name: repository-metadata-version-tag-presence
description: When a RepositoryMetadata subclass stores mainVersion/releaseVersion,
  the TG should verify that calling updateRepositoryMetadata preserves these values
  and does not drop version tags for strings like "LATEST" or "RELEASE". The test
  should create metadata with a main version set to "LATEST" and verify that after
  update, the version tag is still present.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# repository-metadata-version-tag-presence

## Instructions

# Repository Metadata Version Tag Preservation

## Instructions

- WHEN the TG encounters any subclass of `AbstractRepositoryMetadata` that stores `version` strings (like `mainVersion`, `releaseVersion`, or `latestVersion`) and calls `updateRepositoryMetadata(localRepository, remoteRepository)`
- THEN the TG should write a test that:
  1. Creates a `RepositoryMetadata` instance (e.g., `GroupRepositoryMetadata` or `ProjectRepositoryMetadata`)
  2. Sets one of its version fields to the literal string `"LATEST"` (or `"RELEASE"`)
  3. Calls `updateRepositoryMetadata(localRepository, remoteRepository)` on the metadata instance
  4. Verifies that after the update, the version tag (e.g., `<version>` element in the stored metadata XML) is still present and contains the expected value (e.g., `"LATEST"`)
- The TG should verify that the output metadata XML still contains a `<version>` tag with the original value — not that the version was removed or cleared — because the bug causes the version element to be absent from the serialized metadata when the main version string is `"LATEST"`.
- Common pitfall: The TG might only test with numeric version strings like `"1.0"` or `"2.0-SNAPSHOT"` and miss the edge case where the version is the literal keyword `"LATEST"` or `"RELEASE"`. Always include a test case with these special version strings.

**Correct example (what the test should do):**
```java
public void testUpdateRepositoryMetadata_PreservesVersionTagForLATEST() throws Exception {
    var metadata = createMetadata(); // e.g., new GroupRepositoryMetadata(...)
    metadata.setMainVersion("LATEST");
    // populate metadata with some plugin versions
    metadata.setPlugins(...);
    metadata.updateRepositoryMetadata(localRepo, remoteRepo);
    // read back the stored metadata file
    Metadata stored = readMetadataFromRepository(localRepo);
    Assert.assertNotNull("Version tag should be present when main version is 'LATEST'", stored.getVersion());
}
```

**Incorrect example (what the TG might do wrong):**
```java
// BAD: Only tests with a normal version string
public void testUpdateRepositoryMetadata_NormalVersion() throws Exception {
    var metadata = createMetadata();
    metadata.setMainVersion("1.0"); // Safe case — won't trigger the bug
    metadata.updateRepositoryMetadata(localRepo, remoteRepo);
    // This test passes on both buggy and fixed code, missing the bug entirely
}
```