---
name: path-utils-input-validation
description: Detects when PathUtils methods fail to validate invalid paths (e.g.,
  trailing slashes, empty elements, or malformed paths). Apply this skill when testing
  PathUtils utility methods like getName, getParentPath, concat, getAncestorPath,
  or getDepth.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- RELATIVE_PATH_WITH_LEADING_SLASH
test_pattern: EXCEPTION_TEST
---

# path-utils-input-validation

## Instructions

# PathUtils Input Validation Testing

## Instructions

- WHEN the TG encounters `PathUtils.getName(path)`, `PathUtils.getParentPath(path)`, `PathUtils.getAncestorPath(path, nth)`, or `PathUtils.concat(parent, child)` calls in the code under test
- THEN it should test with both valid and **invalid path inputs** to verify that the method throws `AssertionError` (via `assert isValid(path)` ) for malformed inputs
- Include tests for these specific invalid path patterns:
  - **Trailing slash** on a non-root path (e.g. `"invalid/path/"`)
  - **Double slash** in the middle of a path (e.g. `"//"`)
  - **Empty elements** resulting from leading/trailing/double slashes
- For the `concat` method, also test with:
  - A second argument that starts with `/` (e.g., `PathUtils.concat("parent", "/child")`) — this should throw `IllegalArgumentException`
  - Both arguments starting with `/` (e.g., `PathUtils.concat("/parent", "/child")`) — this should throw `IllegalArgumentException`
- Common pitfall: Testing only with well-formed paths like `"/a/b"` or `"a/b"` and missing the case where a path ends with a trailing slash (e.g. `"invalid/path/"`). Both `getName("invalid/path/")` and `getParentPath("invalid/path/")` will trigger an `AssertionError` because the path is not valid (ends with `/` after a non-root path).

### Correct Example

```java
// Test that getName and getParentPath reject invalid trailing-slash paths
try {
    PathUtils.getParentPath("invalid/path/");
    if (assertsEnabled) {
        fail("Expected AssertionError for invalid path with trailing slash");
    }
} catch (AssertionError e) {
    // expected — path ending with '/' is invalid unless it's just "/"
}

try {
    PathUtils.getName("invalid/path/");
    if (assertsEnabled) {
        fail("Expected AssertionError for invalid path with trailing slash");
    }
} catch (AssertionError e) {
    // expected
}

// Test that concat rejects child starting with '/'
try {
    PathUtils.concat("parent", "/child");
    fail("Expected IllegalArgumentException for child starting with '/'");
} catch (IllegalArgumentException e) {
    // expected
}
```

### Incorrect Example (what to avoid)

```java
// BAD: Only tests valid paths, missing the trailing-slash case
assertEquals("child", PathUtils.getName("/parent/child"));
assertEquals("/parent", PathUtils.getParentPath("/parent/child"));

// Does NOT test: getName("invalid/path/") or getParentPath("invalid/path/")
// which would throw AssertionError on the buggy version
```