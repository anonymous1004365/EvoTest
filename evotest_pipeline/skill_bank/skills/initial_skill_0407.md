---
name: plugin-dependency-validation-coverage
description: When validating plugin dependency configurations in Maven models, the
  TG should test that validation rules cover edge cases like null/incomplete groupId,
  artifactId, version, and type fields on plugin dependency objects, not just top-level
  plugin validation. Missing validation of nested plugin dependencies is a common
  bug pattern.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- COLLECTION_OPERATIONS
test_pattern: PARAMETRIC_TEST
---

# plugin-dependency-validation-coverage

## Instructions

# Plugin Dependency Validation Coverage

## Instructions

- WHEN the TG encounters a model validation step that iterates over plugin dependencies (e.g., `build.getPlugins()` → `plugin.getDependencies()` → `Dependency` objects)
- THEN it MUST write a PARAMETRIC_TEST that verifies the validator rejects plugin dependencies with **null or empty `groupId`** (but where the plugin itself has a valid groupId). The test should construct a `Model` with:
  - A `Build` containing a `Plugin` with a valid groupId (e.g. `"org.apache.maven.plugins"`)
  - That `Plugin` containing a `Dependency` with a **null groupId** (all other fields set to non-null values)
  - Expected validation outcome: `modelValidationResult.getErrors()` must contain at least one error message about the missing groupId
- WHEN testing model validation of collections of child objects
- THEN the TG must ensure that the test model is constructed with the child objects set into the parent containers (e.g., `build.setPlugins(...)`, `plugin.setDependencies(...)`) and that the validator's `validate(...)` method is called with the expected parameter types
- Common pitfall: testing only top-level plugin validation while missing that the same validation logic must also apply to **plugin dependencies** — the nested `Dependency` objects inside a `<plugin><dependencies>` element. Another pitfall: constructing the model correctly but not calling `modelValidationResult.getErrors()` or checking for an empty error list when the expected result is that the validator SHOULD flag the missing fields.

### Correct example (Java, JUnit 5):

```java
@Test
void testMissingPluginDependencyGroupId() {
    Model model = new Model();
    model.setGroupId( "test" );
    model.setArtifactId( "test-artifact" );
    model.setVersion( "1.0.0" );

    Build build = new Build();
    Plugin plugin = new Plugin();
    plugin.setGroupId( "org.apache.maven.plugins" );
    plugin.setArtifactId( "maven-compiler-plugin" );

    Dependency dep = new Dependency();
    dep.setGroupId( null );  // missing groupId — should trigger validation error
    dep.setArtifactId( "some-lib" );
    dep.setVersion( "1.0" );

    plugin.setDependencies( Collections.singletonList( dep ) );
    build.setPlugins( Collections.singletonList( plugin ) );
    model.setBuild( build );

    ModelValidationResult result = validator.validate( model );
    assertFalse( result.getErrors().isEmpty() );
    assertTrue( result.getErrors().stream().anyMatch( e -> e.contains( "groupId" ) ) );
}
```

### Incorrect example (missing nested dependency validation):

```java
// BAD: Only tests that plugin itself has groupId, but doesn't test
// plugin's nested dependency objects for missing groupId
@Test
void testPluginGroupIdValidation() {
    Model model = createValidModel();
    Plugin plugin = new Plugin();
    plugin.setGroupId( null );  // tests plugin-level only
    // ... never tests plugin.getDependencies()
    ModelValidationResult result = validator.validate( model );
    // May pass even if plugin dependency validation is broken
}
```