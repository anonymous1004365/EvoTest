---
name: originating-artifact-protection-in-dependency-management
description: When an artifact collector or resolver uses a ManagedVersionMap that
  contains the originating/project artifact, the collector may mutate the originating
  artifact's version. This skill teaches how to test for side-effect protection by
  asserting the originating artifact's version remains unchanged after resolution.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# originating-artifact-protection-in-dependency-management

## Instructions

# Protecting Originating Artifact from Managed Version Side Effects

## Instructions

- WHEN the TG encounters code that creates a `ResolutionNode` from an `originatingArtifact` and then passes both the originating artifact and a `Map` of managed versions (specifically a `ManagedVersionMap`) to a recursive resolution method
- THEN the TG should write a test that:
  1. Creates an `Artifact` instance for the originating/project artifact via `artifactFactory.createBuildArtifact("test-group", "project", "1.0", "jar")` — note the version is "1.0"
  2. Creates a `ManagedVersionMap` containing a managed version entry with the same dependency conflict ID as the originating artifact but with a *different* version (e.g., version "2.0")
  3. Adds a dependent artifact (e.g., via `ArtifactSpec` helper) to the dependency set
  4. Calls `artifactCollector.collect(dependencySet, originatingArtifact, managedVersionMap, ...)` with the proper parameters
  5. **Verifies that the originating artifact's version is unchanged** — use `assertEquals("1.0", originatingArtifact.getVersion())` — the buggy version would mutate the originating artifact to "2.0"
  6. Asserts that the collected result contains expected artifacts (e.g., the project artifact plus the dependency artifact)

- The key assertion must be: `assertEquals("1.0", originatingArtifact.getVersion())` — confirming the originating artifact was NOT mutated by the managed version resolution

- Common pitfalls to avoid:
  - Testing only whether the *resolved artifacts* have correct versions while ignoring the originating artifact's state
  - Omitting the `ManagedVersionMap` parameter (using the overload that doesn't take one), which avoids the bug entirely
  - Using the same version in both the originating artifact and the managed version map — the bug only manifests when they differ
  - Not creating the dependency set with at least one artifact — that triggers the `recurse()` path where the mutation happens

- Example correct test pattern (pseudocode):
```java
Artifact projectArtifact = artifactFactory.createBuildArtifact("test-group", "project", "1.0", "jar");
Artifact dep = createArtifact("a", "1.0").artifact;
Set<Artifact> deps = new HashSet<>();
deps.add(dep);

Artifact managedDep = artifactFactory.createBuildArtifact("test-group", "project", "2.0", "jar");
Map<String, Artifact> managedVersions = new HashMap<>();
managedVersions.put("test-group:project:jar", managedDep);
ManagedVersionMap versionMap = new ManagedVersionMap(managedVersions);

ArtifactResolutionResult result = artifactCollector.collect(deps, projectArtifact, versionMap, localRepo, remoteRepos, source, null, listeners);

assertEquals("Originating artifact version should not be modified", "1.0", projectArtifact.getVersion());
assertTrue(result.getArtifacts().contains(dep));
```

- Example INCORRECT test (would not catch the bug):
```java
// Only checks resolved artifacts, not the originating artifact
assertEquals("2.0", getArtifact("project", result.getArtifacts()).getVersion());
// OR: doesn't include the managed version map at all
artifactCollector.collect(deps, projectArtifact, localRepo, remoteRepos, source, null, listeners);
```