---
name: path-construction-with-trailing-slash
description: When constructing paths by concatenating a parent path with a child name,
  a missing slash separator or an unexpected trailing slash can produce malformed
  paths. This skill teaches how to test that path concatenation methods (like PathUtils.concat
  or manual string concatenation) correctly handle edge cases involving trailing slashes
  on the parent path and proper separator insertion.
code_tags:
- VALIDATION
- PATH_CONSTRUCTION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# path-construction-with-trailing-slash

## Instructions

# Path Construction with Trailing Slash Handling

## Instructions

- WHEN the TG encounters a method that constructs relative or absolute paths by concatenating a parent path and a child name/segment (e.g., using `PathUtils.concat()` or manual `parent + "/" + child` logic)
- THEN it should write a parametric test that covers the following edge cases:
  1. **Parent path with a trailing slash** (e.g., `"/test/"`): verify the concatenation does NOT produce a double-slash or malformed path like `"/test//child"`, and does NOT produce an invalid path like `"/test/"` when the child is empty or null
  2. **Parent path without a trailing slash** (e.g., `"/test"`): this is the normal case — verify the separator is inserted correctly
  3. **Child is empty string or null**: verify the method handles these gracefully without producing a trailing slash path like `"/test/"` or throwing a NullPointerException
  4. **Root parent path** (e.g., `"/"`): verify the method handles this correctly without producing a double-slash like `"//child"`

- The test should verify that the resulting path satisfies a validity check (e.g., `PathUtils.isValid(path)` returns `true`) and is exactly what is expected. On the buggy version, calling the method with a parent that has a trailing slash should produce an invalid path like `"/test/"` which causes downstream failures.

- Common pitfalls to avoid:
  - Testing only the "happy path" where the parent has no trailing slash
  - Assuming path concatenation methods always normalize their inputs
  - Forgetting to test the root path `"/"` as a parent
  - Testing only with String type parameters but not with edge cases like empty strings

### Correct example

```java
@Test
public void testPathConcatenationWithTrailingSlashOnParent() {
    // This test exposes the bug: parent path with trailing slash
    // results in an invalid/empty child path
    String parent = "/test/";
    String child = "a";
    String result = PathUtils.concat(parent, child);
    assertTrue("Path should be valid, but was: " + result, PathUtils.isValid(result));
    // Expected: "/test/a"  (not "/test//a" and not "/test/")
}
```

### Incorrect example (missing the edge case)

```java
@Test
public void testPathConcatenation() {
    // Only tests without trailing slash — misses the bug entirely
    String result = PathUtils.concat("/test", "a");
    assertEquals("/test/a", result);
}
```