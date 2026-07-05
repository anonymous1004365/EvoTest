---
name: classpath-elements-null-safety
description: WHEN calling getCompileClasspathElements(), getSystemClasspathElements(),
  getRuntimeClasspathElements(), or getTestClasspathElements() on a minimal/unconfigured
  MavenProject, THEN verify no null elements appear in the returned lists. The buggy
  version could include null entries when the Build's outputDirectory was not set.
code_tags:
- NULL_CHECK
test_pattern: STATE_TEST
---

# classpath-elements-null-safety

## Instructions

# Classpath Elements Null Safety

## Instructions

- WHEN the TG encounters methods that return `List<String>` representing classpath elements from `MavenProject` (specifically `getCompileClasspathElements()`, `getSystemClasspathElements()`, `getRuntimeClasspathElements()`, or `getTestClasspathElements()`), AND the project is constructed without any Build configuration (e.g., `new MavenProject()` or `new MavenProject(model)` where model has no Build),
- THEN the TG should test that the returned `List<String>` does NOT contain any null elements. Use `assertFalse(elements.contains(null))` or equivalent to verify.
- Include a specific test that creates a `MavenProject` with `new MavenProject()` and calls each of the four `*ClasspathElements()` methods, asserting no nulls in the returned list.
- The buggy version returned lists containing null elements when the project's Build outputDirectory was undefined (null). The fixed version excludes nulls from the list.
- Common pitfall: Testing only that the list is not null or not empty, but not checking that individual elements are non-null. The list may be non-empty but still contain null entries.
- Common pitfall: Only testing `getCompileClasspathElements()` and forgetting the other three methods (`getSystemClasspathElements()`, `getRuntimeClasspathElements()`, `getTestClasspathElements()`).

**Correct example:**
```java
MavenProject p = new MavenProject();
assertFalse(p.getCompileClasspathElements().contains(null));
assertFalse(p.getSystemClasspathElements().contains(null));
assertFalse(p.getRuntimeClasspathElements().contains(null));
assertFalse(p.getTestClasspathElements().contains(null));
```

**Incorrect example (would miss the bug):**
```java
MavenProject p = new MavenProject();
assertNotNull(p.getCompileClasspathElements());  // passes even with null elements
```