---
name: invalid-parent-inheritance-validation
description: When building parent-child project models in Maven, the DefaultProjectBuilder
  silently swallows invalid parent references. Test that constructing a MavenProject
  with an unresolvable/invalid parent reference throws an appropriate exception instead
  of silently continuing.
code_tags:
- INHERITANCE_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# invalid-parent-inheritance-validation

## Instructions

# Invalid Parent Inheritance Validation

## Instructions

WHEN the TG encounters a `MavenProject` being constructed with a parent reference that cannot be resolved (e.g., the parent POM is missing, has invalid coordinates, or references a non-existent artifact),
THEN the TG should test that building such a project fails with an appropriate exception rather than silently swallowing the error.

**Concrete details:**
- The buggy code in `DefaultProjectBuilder.java` (around line 652) catches `ProjectBuildingException` when trying to build the parent project and merely logs a warning: `"Failed to build parent project for " + project.getId()`. It does NOT rethrow the exception or propagate the error.
- The test should construct a `MavenProject` instance (or use `ProjectBuilder`) where `getParentFile()` returns a valid but unresolvable POM, or the parent coordinates (`groupId:artifactId:version`) reference an artifact that does not exist.
- The test should verify that an exception (e.g., `ProjectBuildingException`, `IllegalStateException`, or similar) is thrown when the invalid parent is encountered.
- Use `@Test(expected = ...)` or `assertThrows(ProjectBuildingException.class, () -> ...)` to verify the expected failure.

**Common pitfalls to avoid:**
- Testing only valid parent scenarios — the bug is specifically about invalid parent handling.
- Assuming that a warning log message is sufficient error handling — the test must verify that the build actually fails.
- Constructing a `MavenProject` with `new MavenProject()` without setting up the parent reference — the test must set up the parent model so that resolution is attempted.
- Using mocked parent resolution that returns successfully — the test must trigger actual failure (e.g., unresolvable remote parent).

**Correct example:**
```java
@Test
public void testInvalidParent() {
    ProjectBuildingRequest request = new DefaultProjectBuildingRequest();
    // ... set up request with repository session, etc.
    assertThrows(ProjectBuildingException.class, () -> {
        projectBuilder.build(
            new File("src/test/resources/projects/invalid-parent/pom.xml"), request
        );
    });
}
```

**Incorrect example (does not catch the bug):**
```java
@Test
public void testInvalidParent() {
    ProjectBuildingRequest request = new DefaultProjectBuildingRequest();
    // ... setup
    MavenProject project = projectBuilder.build(
        new File("src/test/resources/projects/invalid-parent/pom.xml"), request
    ).getProject();
    // Bug: build succeeds silently with null/invalid parent
    assertNotNull(project.getParent());
    // This assertion passes on buggy code because project.getParent() is null
}
```