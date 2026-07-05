---
name: latest-main-version-storage-guard
description: When storing repository metadata that uses "LATEST" as the main version,
  the metadata should NOT be stored/written because "LATEST" is a placeholder that
  must be resolved dynamically. This skill helps write tests that catch incorrect
  storage of metadata with LATEST main version.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# latest-main-version-storage-guard

## Instructions

# LATEST Main Version Storage Guard

## Instructions

- WHEN the TG encounters a method that stores/persists repository metadata (e.g., `RepositoryMetadataManager.store(...)`, `AbstractRepositoryMetadata.store(...)`, or any method that writes metadata to a repository)
- AND the metadata object has a `getMetadata()` method returning a `Metadata` object with a `getVersioning()` method returning a `Versioning` object that has `getLatest()` or `getMainVersion()` (e.g., `metadata.getMetadata().getVersioning().getMainVersion()`)
- THEN the TG should test that when the **main version** (or latest version) of the metadata is set to the placeholder string `"LATEST"` (which is a constant like `Artifact.LATEST_VERSION`), the store should **NOT** persist/write the metadata (e.g., no call to the underlying write mechanism, no file created)
- The test should verify that the store method either:
  1. Throws an appropriate exception (e.g., `RepositoryMetadataStoreException`), OR
  2. Silently returns without performing any write operation (e.g., a mocked writer receives no call)
- The test should specifically construct a `Metadata` object whose `versioning.mainVersion` (or `versioning.latest`) is set to `Artifact.LATEST_VERSION` (i.e., the string `"LATEST"`)
- Common pitfalls to avoid:
  - Testing only with regular version strings like `"1.0"` or `"2.0-SNAPSHOT"` and missing the `"LATEST"` case
  - Assuming that `"LATEST"` is a valid version to store — it is a meta-version that must be resolved at runtime
  - Not checking the specific behavior (exception vs. no-op) — verify that no write occurs rather than just catching any exception
  - Using `"latest"` (lowercase) instead of `"LATEST"` — the constant is uppercase

### Correct Example (JUnit 4 style)

```java
@Test
public void testShouldNotStoreWhenMainVersionIsLATEST() {
    // Arrange
    Metadata metadata = new Metadata();
    Versioning versioning = new Versioning();
    versioning.setMainVersion(Artifact.LATEST_VERSION);  // "LATEST"
    metadata.setVersioning(versioning);
    
    ArtifactRepository repository = mock(ArtifactRepository.class);
    RepositoryMetadata repoMetadata = new ArtifactRepositoryMetadata(metadata);

    // Act & Assert
    try {
        repositoryMetadataManager.store(repoMetadata, repository);
        fail("Expected RepositoryMetadataStoreException to be thrown");
    } catch (RepositoryMetadataStoreException e) {
        // Expected — store should fail/be rejected for LATEST main version
    }
    
    // Or, if the method is void and silently returns:
    // verifyNoInteractions(writer);
}
```

### Incorrect Example (what to avoid)

```java
// BAD: Only tests with a real version, misses the LATEST placeholder
@Test
public void testStoreWithVersion1_0() {
    Metadata metadata = new Metadata();
    Versioning versioning = new Versioning();
    versioning.setMainVersion("1.0");  // This is fine, but doesn't cover LATEST
    metadata.setVersioning(versioning);
    
    // The bug would NOT be caught by this test
    repositoryMetadataManager.store(repoMetadata, repository);
}
```