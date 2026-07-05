---
name: dependency-filter-mutation-immutability
description: WHEN converting Maven Dependencies to Artifacts using createArtifacts(),
  THEN verify that the dependency filter (ArtifactFilter) is not mutated or shared
  across artifacts. This skill helps catch bugs where the inherited filter is wrapped
  (e.g. using AndArtifactFilter) and the mutation leaks state between unrelated dependency
  artifacts.
code_tags:
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# dependency-filter-mutation-immutability

## Instructions

# Dependency Filter Mutation / Immutability

## Instructions

- **WHEN** the TG encounters code that creates `Artifact` objects from `Dependency` objects, especially via `MavenMetadataSource.createArtifacts()` or similar conversion logic that involves an `ArtifactFilter` (dependency filter):
  - **THEN** the TG should write a test that creates **multiple** `Dependency` objects, each with potentially different exclusions or no exclusions, and a shared `ArtifactFilter` (e.g., `ScopeArtifactFilter`), converts them to `Artifact`s, and then **asserts that the dependency filter on one artifact has not been mutated by processing another artifact**.

- **WHEN** the test verifies that a dependency filter has not been mutated between artifacts:
  - **THEN** it should use `assertSame()` (reference identity check) to confirm the original filter object is still set on the artifact that was not supposed to have its filter modified, OR it should verify that the filter type/class on the unaffected artifact remains the original type (e.g., `ScopeArtifactFilter`) rather than a composite type (e.g., `AndArtifactFilter`).

- **WHEN** `createDependencyFilter()` wraps the inherited filter in an `AndArtifactFilter`:
  - **THEN** the TG must verify that the wrapping mutation is applied only to the intended artifact's filter, and that other artifacts created from dependencies without exclusions still hold the **original** unchanged filter reference.

- **Common Pitfalls to avoid**:
  - Testing only a single dependency conversion — this will miss cross-artifact filter mutation bugs.
  - Using `assertEquals()` instead of `assertSame()` — the bug is about reference identity/object mutation, not value equality.
  - Relying solely on `equals()` comparisons — the bug involves the actual `ArtifactFilter` object being mutated (wrapped in an `AndArtifactFilter`), not just logically equivalent.
  - Assuming that creating artifacts sequentially is safe — the mutation may happen on a mutable filter field, affecting previously created artifacts retroactively.

### Example Test (Correct)

```java
public void testShouldNotCarryExclusionsOverFromDependencyToDependency() throws Exception
{
    // Create two dependencies, one with exclusions and one without
    Dependency dep1 = new Dependency();
    dep1.setGroupId( "test" );
    dep1.setArtifactId( "test-artifact" );
    dep1.setVersion( "1" );
    dep1.setType( "jar" );

    Exclusion exc = new Exclusion();
    exc.setGroupId( "test" );
    exc.setArtifactId( "test-artifact3" );
    dep1.addExclusion( exc );

    Dependency dep2 = new Dependency();
    dep2.setGroupId( "test" );
    dep2.setArtifactId( "test-artifact2" );
    dep2.setVersion( "1" );
    dep2.setType( "jar" );

    List<Dependency> deps = new ArrayList<>();
    deps.add( dep1 );
    deps.add( dep2 );

    ArtifactFactory factory = lookup( ArtifactFactory.class );
    ArtifactFilter dependencyFilter = new ScopeArtifactFilter( Artifact.SCOPE_COMPILE );

    Set<Artifact> result = MavenMetadataSource.createArtifacts( factory, deps, null, dependencyFilter );

    for ( Artifact artifact : result )
    {
        if ( "test-artifact2".equals( artifact.getArtifactId() ) )
        {
            ArtifactFilter filter = artifact.getDependencyFilter();
            // The artifact WITHOUT exclusions must still hold the ORIGINAL filter (identity check)
            assertSame( "Dependency filter was mutated by processing other dependencies. " +
                        "Expected the original ScopeArtifactFilter but got: " + filter,
                        dependencyFilter, filter );
        }
    }
}
```

### Example Test (Incorrect — would miss this bug)

```java
// WRONG: Only tests a single dependency, won't detect cross-artifact filter mutation
public void testSingleDependencyFilter() throws Exception {
    Dependency dep = new Dependency();
    dep.setGroupId( "test" );
    dep.setArtifactId( "test-artifact" );
    dep.setVersion( "1" );
    // No exclusions
    
    List<Dependency> deps = Collections.singletonList(dep);
    ArtifactFilter filter = new ScopeArtifactFilter(Artifact.SCOPE_COMPILE);
    Set<Artifact> result = MavenMetadataSource.createArtifacts(factory, deps, null, filter);
    
    // This passes even with the bug since only one artifact exists
    Artifact artifact = result.iterator().next();
    assertSame(filter, artifact.getDependencyFilter()); // Still passes on buggy code!
}
```