---
name: classpath-elements-null-check
description: When testing getCompileClasspathElements, getRuntimeClasspathElements,
  getTestClasspathElements, or getSystemClasspathElements on MavenProject with no
  Build configuration, verify no null elements appear in returned lists. This skill
  prevents null element bugs when output directories are undefined.
code_tags:
- NULL_CHECK
test_pattern: STATE_TEST
---

# classpath-elements-null-check

## Instructions

# Classpath Elements Return No Nulls for Undefined Output Directories

## Instructions

- WHEN the TG encounters a `MavenProject` instance that has never had its `Build` object configured (i.e., no `build` element set) and the code under test calls one of `getCompileClasspathElements()`, `getSystemClasspathElements()`, `getRuntimeClasspathElements()`, or `getTestClasspathElements()`
- THEN the TG should construct a fresh `MavenProject` (using `new MavenProject()` or `new MavenProject(new Model())` without setting any `Build`) and assert that the returned `List<String>` from each of those four methods contains **no null elements**.
- The concrete assertion should be `assertFalse(elements.contains(null))` after calling each method, because the buggy version may insert `null` into the list when the output directory is undefined.
- Common pitfall: Testing only one of the four classpath methods (e.g., only `getCompileClasspathElements()`) instead of all four (`getCompileClasspathElements`, `getSystemClasspathElements`, `getRuntimeClasspathElements`, `getTestClasspathElements`), missing the fact that all four methods share the same null-element bug.
- Common pitfall: Using `assertNotNull` on the list itself, which passes even if `null` values are inside the list. The test must verify list contents by checking `elements.contains(null)`.

**Correct example:**
```java
public void testUndefinedOutputDirectory() throws Exception {
    MavenProject p = new MavenProject();
    assertFalse(p.getCompileClasspathElements().contains(null));
    assertFalse(p.getSystemClasspathElements().contains(null));
    assertFalse(p.getRuntimeClasspathElements().contains(null));
    assertFalse(p.getTestClasspathElements().contains(null));
}
```

**Incorrect example:**
```java
public void testUndefinedOutputDirectory() throws Exception {
    MavenProject p = new MavenProject();
    assertNotNull(p.getCompileClasspathElements());  // Bug: passes even if list contains null
}
```