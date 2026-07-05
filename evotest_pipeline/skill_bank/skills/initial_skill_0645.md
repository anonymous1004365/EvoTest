---
name: path-depth-to-root-boundary-calculation
description: When testing path depth calculation methods, verify edge cases around
  root path ("/") and empty string ("") boundaries. The buggy code returned depth
  1 for the root path "/" instead of the correct 0.
code_tags:
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# path-depth-to-root-boundary-calculation

## Instructions

# Path Depth Root Boundary Calculation

## Instructions

- WHEN the TG encounters a `getDepth(String path)` method (like `org.apache.jackrabbit.oak.commons.PathUtils.getDepth`) that calculates element count in a path
  - THEN the TG MUST test the boundary case where `path` is `"/"` (root path) and verify that `getDepth("/")` returns `0` (not `1`)
  - THEN the TG MUST also test the empty string `""` boundary case and verify that `getDepth("")` returns `0`
  - THEN the TG MUST test single-element paths like `"/a"` (absolute) and `"a"` (relative) and verify they return `1`

- Common pitfalls to avoid:
  - Testing only relative paths (like `"a"`, `"a/b"`) without testing the absolute root path `"/"` boundary
  - Testing only absolute paths without relative ones
  - Assuming `"/"` has one element — the root has zero elements by convention
  - Failing to test the empty string `""` which should also have depth 0

- Correct test pattern:
```java
// Correct: tests all boundary cases
assertEquals(0, PathUtils.getDepth("/"));   // root path boundary
assertEquals(0, PathUtils.getDepth(""));    // empty path boundary
assertEquals(1, PathUtils.getDepth("/a"));  // single element absolute
assertEquals(1, PathUtils.getDepth("a"));   // single element relative
assertEquals(2, PathUtils.getDepth("/a/b"));// two elements absolute
assertEquals(2, PathUtils.getDepth("a/b")); // two elements relative
```

- Incorrect test pattern (missing the root boundary):
```java
// WRONG: missing the "/" root and "" empty boundary tests
assertEquals(1, PathUtils.getDepth("/a"));    // may pass on buggy code too
assertEquals(2, PathUtils.getDepth("a/b"));   // may pass on buggy code too
// No test for getDepth("/") == 0 → bug would go undetected!
```