---
name: scope-update-preserves-dependency-resolution
description: When testing dependency resolution logic that updates artifact scopes
  during recursive traversal, verify that scope-changing operations on transitive
  dependencies do not cause those dependencies to be dropped from the resolution result.
  This skill is critical when testing artifact collectors that manage scope transitions
  in dependency graphs.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
- STATE_MUTATION
- ORDER_DEPENDENCY
- VALIDATION
test_pattern: STATE_TEST
---

# scope-update-preserves-dependency-resolution

## Instructions

# Scope Update Preserves Dependency Resolution

## Instructions

- WHEN the TG encounters a dependency resolution or artifact collection method that modifies artifact scopes (e.g., setting `artifactScope` on an `Artifact` or `ResolutionNode` during recursive traversal)
- THEN it should write a test that constructs a dependency graph where a transitive dependency has a narrower scope (e.g., "test") that gets updated to a broader scope (e.g., "compile") during resolution, and verify that the artifact with the updated scope is still present in the resolution result
- Test by building a dependency tree like: A depends on B (compile), B depends on C (test). During traversal, C's scope gets updated when it's resolved. Assert that C is still included in the resulting `ArtifactResolutionResult.getArtifacts()` set and has the updated scope value
- Include an assertion with a descriptive message such as `assertNotNull("MNG-1895 Dependency was not added to resolution", artifact)` to verify the artifact was not dropped after scope mutation
- Common mistake: Testing only the scope value change without verifying the artifact is still retained in the result set. The bug occurs when scope updates cause the resolution logic to incorrectly filter out or skip adding the artifact back into the results
- Common mistake: Assuming that any artifact visiting a resolution node will always be included in the final result without checking that scope mutations don't interfere with the node's inclusion logic
- Common mistake: Testing scope updates only on direct dependencies rather than transitive (non-root-child) dependencies where the bug manifests

```java
// CORRECT: Tests that scope update on transitive dependency preserves it in resolution
public void testScopeUpdatePreservesTransitiveDependency() throws Exception {
    ArtifactSpec a = createArtifactSpec("a", "1.0");
    ArtifactSpec b = a.addDependency("b", "1.0");
    ArtifactSpec c = b.addDependency("c", "1.0", Artifact.SCOPE_TEST); // transitive, test scope
    
    ArtifactResolutionResult res = collect(a);
    
    Artifact cArtifact = getArtifact("c", res.getArtifacts());
    assertNotNull("Dependency C was lost after scope update during resolution", cArtifact);
    assertEquals("Scope should be updated", Artifact.SCOPE_COMPILE, cArtifact.getScope());
}
```

```java
// INCORRECT: Only checks scope value but doesn't verify artifact retention
public void testScopeUpdate_bad() throws Exception {
    ArtifactSpec a = createArtifactSpec("a", "1.0");
    ArtifactSpec b = a.addDependency("b", "1.0");
    ArtifactSpec c = b.addDependency("c", "1.0", Artifact.SCOPE_TEST);
    
    ArtifactResolutionResult res = collect(a);
    // Missing: assertNotNull check for artifact "c" in result
    // The scope might update, but the artifact might not be in the result set
}
```