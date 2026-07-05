---
name: dependency-version-validation
description: When validating Maven model dependency versions, the TG should test both
  valid and invalid version inputs (e.g., ranges, expressions, placeholders) to ensure
  proper validation logic catches malformed or unresolvable versions. This skill applies
  specifically to Dependency and DependencyManagement section validation.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STRING_PARSING_NORMALIZATION
- VALIDATION
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: EXCEPTION_TEST
---

# dependency-version-validation

## Instructions

# Dependency Version Validation

## Instructions

- WHEN the TG encounters code that validates dependency version fields in a Maven model (e.g., `Dependency.getVersion()`, `version` field in `<dependency>` or `<dependencyManagement>` sections)
- THEN the TG should write tests that exercise the validation with multiple categories of version inputs:
  - **Invalid/empty versions**: `null`, empty string `""`, and purely whitespace strings like `"  "` — these should trigger a validation failure (model error)
  - **Version range expressions**: e.g., `"["2.0.0","3.0.0")"` — these should NOT trigger false validation failures
  - **Placeholder/system expressions**: e.g., `${some.version}` — these should be treated as valid and not fail validation
  - **Non-range but resolvable versions**: e.g., `"1.0"`, `"2.0.1"` — these should pass validation
- The test should verify that an appropriate `ModelValidationViolation` or `ModelBuildingException`/`ModelBuildingResult` is produced with error messages referencing the bad version value, containing phrases like `"version"` or referencing the offending dependency
- Common pitfalls to avoid:
  - Testing only `null` or only empty string — the bug may only surface with a specific bad value pattern
  - Forgetting that version ranges (`[1.0,2.0)`) are valid Maven expressions and should NOT trigger validation errors
  - Assuming validation only occurs on direct dependencies and not also on `dependencyManagement` entries (both paths need coverage)
  - Not checking the actual error message content to confirm the validator complained about the version vs. some other field

### Correct Example (Java)
```java
@Test
public void testBadDependencyVersion() {
    Model model = new Model();
    model.setGroupId( "test" );
    model.setArtifactId( "test" );
    model.setVersion( "1.0" );

    Dependency dep = new Dependency();
    dep.setGroupId( "org.apache" );
    dep.setArtifactId( "some-artifact" );
    dep.setVersion( "" );  // Empty version — should fail

    model.getDependencies().add( dep );

    List<ModelValidationViolation> violations = validateRawModel( model );
    assertTrue( violations.stream().anyMatch( v -> v.getMessage().contains( "version" ) ) );
}
```

### Incorrect Example (Java)
```java
// BAD: Testing only null version but the real bug might be empty string or whitespace
@Test
public void testBadDependencyVersion() {
    Model model = baseModel();
    Dependency dep = new Dependency();
    dep.setGroupId( "org.apache" );
    dep.setArtifactId( "some-artifact" );
    dep.setVersion( null );  // Only null, missing other patterns

    model.getDependencies().add( dep );

    List<ModelValidationViolation> violations = validateRawModel( model );
    assertFalse( violations.isEmpty() );  // Too vague — should check content
}
```