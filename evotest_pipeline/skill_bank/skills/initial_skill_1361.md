---
name: path-depth-windows-drive-counting
description: When testing path depth calculations, check that Windows-style drive
  letters (e.g., C:/) are not counted as an extra path segment. The `depth()` method
  should only count directory separators, not the leading `/` prepended for Windows
  drives.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONCURRENCY
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# path-depth-windows-drive-counting

## Instructions

# Path Depth Windows Drive Letter Counting

## Instructions

- WHEN the TG encounters a method like `depth()` that counts path segments by splitting on `/` or iterating over the path string
- THEN the TG should test with Windows-style paths containing drive letters (e.g., `"C:/my/windows/path"`)
- The TG should verify that the `depth()` of `new Path("C:/my/windows/path")` returns 3 (the number of directory segments: `my`, `windows`, `path`), NOT 4 (which would incorrectly count the leading `/C:` as an extra segment)
- The TG should use `assertEquals(3, new Path("C:/my/windows/path").depth())` to catch the bug
- Common pitfall: testing depth only with UNIX-style paths (e.g., `/my/path`) misses this bug. The bug is that `normalizePath()` converts `"C:/my/windows/path"` to `"/C:/my/windows/path"` (prepending `/` for Windows drives), and a naive `depth()` implementation that simply counts `/` separators will count the leading `/C:` as an extra segment.

### Correct test example
```java
// This would catch the bug on the buggy version (expected:3, actual:4)
assertEquals(3, new Path("C:/my/windows/path").depth());

// Also test edge cases
assertEquals(0, new Path("/").depth());
assertEquals(1, new Path("/my").depth());
assertEquals(2, new Path("/my/path").depth());
assertEquals(4, new Path("/C:/my/windows/path").depth()); // UNCLEAR: depends on whether /C: is a drive prefix
```

### Incorrect test (would NOT catch the bug)
```java
// Only testing UNIX paths — misses Windows drive letter issue
assertEquals(2, new Path("/my/path").depth());
assertEquals(3, new Path("/my/fancy/path/").depth());
assertEquals(0, new Path("/").depth());
```