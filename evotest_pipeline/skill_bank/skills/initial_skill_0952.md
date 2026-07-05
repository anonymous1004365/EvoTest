---
name: artifact-scope-update-ordering
description: When testing artifact resolution logic that updates scope/version based
  on multiple dependency paths, the order of processing can determine which version
  wins. This skill teaches testing both orderings to catch update-ordering bugs.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# artifact-scope-update-ordering

## Instructions

# Artifact Scope/Version Update Ordering

## Instructions

- WHEN the TG encounters artifact resolution logic that updates version or scope of an existing artifact in a collection (e.g., `versionMap.put` or `artifact.setVersion`/`artifact.setScope`) based on traversing multiple dependency paths
- THEN the TG should write a test that verifies the final resolved version/scope is correct REGARDLESS of the traversal ordering. Specifically:
  - Create two dependency paths to the same artifact (same groupId:artifactId) with different versions (e.g., version "1.0" and version "2.0")
  - Test that when the "correct" version (e.g., "1.0") is encountered FIRST and the "incorrect" version (e.g., "2.0") is encountered SECOND, the final result correctly selects version "1.0"
  - ALSO test that when the "incorrect" version (e.g., "2.0") is encountered FIRST and the "correct" version (e.g., "1.0") is encountered SECOND, the final result STILL correctly selects version "1.0"
  - The test should use concrete artifact instances (e.g., `new DefaultArtifact("group", "artifact", "1.0", "compile", "jar", null, ...)`) and verify the resolution result's version string via assertions like `assertEquals("1.0", resultArtifact.getVersion())`
- Common pitfalls to avoid:
  - Testing only one ordering of dependency traversal (the order in which the tree is flattened may not be deterministic and may change across environments)
  - Assuming that the first-encountered artifact version is always the one that wins; the resolution logic may update (mutate) the already-placed artifact when a "better" version is found later
  - Not verifying the final state of the resolved artifact after all paths have been processed
  - Using mock objects that don't properly simulate the `Artifact` state mutation (setVersion, setScope) behavior

### Correct example (in Java, JUnit 4 style):
```java
@Test
public void testVersionUpdateOrdering() {
    // Scenario: artifact A has version 1.0 via path 1, version 2.0 via path 2
    // The correct version is 1.0 (e.g., due to scope/nearest-wins rules)
    
    // Set up the collector
    DefaultArtifactCollector collector = new DefaultArtifactCollector();
    
    // Create the root artifact
    Artifact root = new DefaultArtifact("group", "root", "1.0", "compile", "jar", null, new DefaultArtifactHandler("jar"));
    
    // Create dependency path artifacts
    Artifact depV1 = new DefaultArtifact("group", "artifact", "1.0", "compile", "jar", null, new DefaultArtifactHandler("jar"));
    Artifact depV2 = new DefaultArtifact("group", "artifact", "2.0", "compile", "jar", null, new DefaultArtifactHandler("jar"));
    
    // ... set up dependency tree with both versions, where v1 should be selected ...
    
    // Collect
    ArtifactResolutionResult result = collector.collect(...);
    
    // Verify the correct version wins
    assertEquals("1.0", result.getArtifacts().iterator().next().getVersion());
}
```

### Incorrect example (fragile, order-dependent):
```java
// WRONG: Assumes artifacts are always processed in one specific order
@Test
public void testVersionUpdate() {
    // Only sets up one ordering
    List<Artifact> deps = new ArrayList<>();
    deps.add(new DefaultArtifact("group", "artifact", "1.0", "compile", "jar", null, ...));
    deps.add(new DefaultArtifact("group", "artifact", "2.0", "compile", "jar", null, ...));
    
    // Only tests this one specific ordering
    ArtifactResolutionResult result = collector.collect(deps, ...);
    
    // This passes only if version 1.0 is the first encountered AND wins
    assertEquals("1.0", result.getArtifacts().iterator().next().getVersion());
}
```