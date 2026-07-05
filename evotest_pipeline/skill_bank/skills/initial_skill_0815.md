---
name: snapshot-version-deterministic-resolution
description: When resolving SNAPSHOT artifact versions with timestamped builds, the
  resolved version must be deterministic and consistent across multiple resolutions
  within the same session. This skill teaches how to test that version resolution
  produces predictable, reproducible results for SNAPSHOT dependencies.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- SNAPSHOT_VERSION_HANDLING
- VERSION_RESOLUTION
- DATA_INTEGRITY_AND_CORRECTNESS
test_pattern: STATE_TEST
---

# snapshot-version-deterministic-resolution

## Instructions

# Snapshot Version Deterministic Resolution

## Instructions

- WHEN the TG encounters code that resolves Maven artifact descriptors (e.g., `DefaultArtifactDescriptorReader`) and handles SNAPSHOT version dependencies (versions ending with `-SNAPSHOT`)
- THEN the TG should write a test that:
  1. Configures a test repository containing SNAPSHOT artifacts with timestamped build versions (e.g., `0.4.0-20130404.090532-2`)
  2. Requests the artifact descriptor for a SNAPSHOT artifact (e.g., `org.apache.maven.plugins:maven-core-it-support:0.4.0-SNAPSHOT`)
  3. Asserts that the resolved version in the returned artifact descriptor's `Artifact` matches the expected timestamped build number — **not** just that the descriptor loads without error
  4. Verifies the exact resolved version string (e.g., `0.4.0-20130404.090532-2`) is deterministic for a given repository state
- WHEN the resolution produces an incorrect snapshot build number (e.g., `0.4.0-20130404.093655-3` instead of `0.4.0-20130404.090532-2`)
- THEN the TG should assert that the test fails with a clear message showing the mismatch between expected and actual resolved version
- Common pitfalls to avoid:
  - **Testing only that a descriptor exists** — The bug is about the specific resolved version string being wrong, not about the descriptor loading failing entirely
  - **Using non-SNAPSHOT versions** — SNAPSHOT resolution with timestamped builds is the specific scenario that triggers the bug
  - **Forgetting to set up the repository session** — The test must properly configure `RepositorySystemSession` and remote repositories so the reader resolves the SNAPSHOT from the test fixture, not from Maven Central
  - **Ignoring the `Artifact.getVersion()` vs `Artifact.getBaseVersion()` distinction** — The test must check the resolved version (which includes the timestamp/build number), not just the base version

### Correct Example

```java
@Test
void testMng5459() throws Exception {
    RepositorySystem repoSystem = newRepositorySystem();
    RepositorySystemSession session = newSession( repoSystem );

    ArtifactDescriptorReader reader = new DefaultArtifactDescriptorReader( repoSystem, session );

    Artifact artifact = new DefaultArtifact(
        "org.apache.maven.plugins", "maven-core-it-support", "0.4.0-SNAPSHOT" );

    ArtifactDescriptorRequest request = new ArtifactDescriptorRequest();
    request.setArtifact( artifact );
    request.addRepository( newTestRepository() );

    ArtifactDescriptorResult result = reader.readArtifactDescriptor( session, request );

    assertEquals( "0.4.0-20130404.090532-2", result.getArtifact().getVersion() );
}
```

### Incorrect Example (would NOT catch the bug)

```java
@Test
void testSnapshotResolution() throws Exception {
    RepositorySystem repoSystem = newRepositorySystem();
    RepositorySystemSession session = newSession( repoSystem );

    ArtifactDescriptorReader reader = new DefaultArtifactDescriptorReader( repoSystem, session );

    Artifact artifact = new DefaultArtifact(
        "org.apache.maven.plugins", "maven-core-it-support", "0.4.0-SNAPSHOT" );

    ArtifactDescriptorRequest request = new ArtifactDescriptorRequest();
    request.setArtifact( artifact );
    request.addRepository( newTestRepository() );

    ArtifactDescriptorResult result = reader.readArtifactDescriptor( session, request );

    // ❌ Only checks that a descriptor was found — does NOT verify the specific resolved version
    assertNotNull( result.getArtifact() );
    assertFalse( result.hasProblems() );
}
```