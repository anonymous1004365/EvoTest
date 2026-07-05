---
name: duplicate-plugin-validation
description: When validating that plugin declarations in a Maven POM are unique, test
  that the validator catches duplicate plugins across both the build.plugins and build.pluginManagement
  sections, as well as within profile-specific build sections.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# duplicate-plugin-validation

## Instructions

# Duplicate Plugin Validation in Maven POM Model

## Instructions

- WHEN the TG encounters code that validates plugin declarations in Maven model building (e.g., `validate20RawPlugins` or `DefaultModelValidator` methods that check for duplicate plugins)
- THEN it should test with at least TWO identical plugin declarations (same groupId and artifactId) in the same `<plugins>` block to verify that duplicate detection produces a validation error. The test must also cover duplicate plugins in `<pluginManagement><plugins>` separately and in profile-specific `<build><plugins>` / `<build><pluginManagement><plugins>` sections.
- The test should verify that `SimpleProblemCollector.getErrors()` or `getFatals()` contains messages such as `"must be unique but found duplicate declaration of plugin"`.
- Common mistake: only testing duplicate plugins in the main `<build><plugins>` section and forgetting to test `<build><pluginManagement><plugins>` and profile-level plugin declarations. Another mistake: using a POM with plugins that have different `groupId` or `artifactId` values, which would NOT trigger a duplicate violation.

### Correct Example

```java
public void testDuplicatePlugin() throws Exception {
    SimpleProblemCollector result = validateRaw("duplicate-plugin.xml");
    // Expect at least 4 errors:
    // - build.plugins.plugin (duplicate)
    // - build.pluginManagement.plugins.plugin (duplicate)
    // - profiles.profile[test].plugins.plugin (duplicate)
    // - profiles.profile[test].pluginManagement.plugins.plugin (duplicate)
    assertTrue(result.getErrors().size() >= 4);
    assertContains(result.getErrors().get(0), "duplicate declaration of plugin");
}
```

### Incorrect Example

```java
public void testDuplicatePlugin() throws Exception {
    SimpleProblemCollector result = validateRaw("duplicate-plugin.xml");
    // Wrong: only checks for 1 error instead of 4+
    assertViolations(result, 0, 1, 0);
    // Wrong: checking for a generic error message that doesn't mention "duplicate"
    assertContains(result.getErrors().get(0), "plugin");
}
```