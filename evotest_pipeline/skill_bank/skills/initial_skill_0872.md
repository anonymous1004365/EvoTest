---
name: windows-path-isabsolute-validation
description: WHEN testing path.isAbsolute() with Windows-style paths (e.g., "C:" without
  trailing slash), THEN verify the method correctly identifies them as relative, not
  absolute. This applies to any Path class that supports Windows drive letter notation.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MODIFICATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# windows-path-isabsolute-validation

## Instructions

# Windows Path isAbsolute() Validation

## Instructions

- WHEN the TG encounters a `Path` class that has an `isAbsolute()` method and supports Windows-style drive letter paths (e.g., "C:/path", "C:"):
  - THEN test `isAbsolute()` with `"C:"` (drive letter without separator or trailing slash). On the buggy version, this returns `true` (incorrectly marking it as absolute). The correct behavior is to return `false` since a drive letter alone (like `"C:"`) is a relative path on Windows.
  - THEN also test combinations like `"C:my\\relative\\path"` (expected `false`), `"C:/"` (expected `true`), `"/C:/"` (expected `true`), and `"\\\\myServer\\myDir"` (UNC paths, expected `true`).
  - Use `assertTrue`/`assertFalse` to verify the boolean return value of `isAbsolute()`.

- Common pitfalls to avoid:
  - Do NOT assume that `"C:"` is an absolute path — it is a relative path that resolves against the current directory of the C: drive.
  - Do NOT test only with paths that start with a slash — Windows drive-based paths need their own test cases.
  - Do NOT miss the edge case where `"C:/"` is absolute (has trailing slash and separator), but `"C:"` alone is not.
  - Do NOT assume all drive-letter-formatted paths are absolute — the presence of a colon does not imply an absolute path.

### Example (correct):
```java
// Test Windows path isAbsolute behavior
Path p = new Path("C:");                // Drive letter only — relative
assertFalse(p.isAbsolute());

p = new Path("C:/");                    // Drive letter with slash — absolute
assertTrue(p.isAbsolute());

p = new Path("/c:/my/dir");             // Slash-prefixed drive letter — absolute
assertTrue(p.isAbsolute());

p = new Path("C:my\\relative\\path");   // Drive-relative path — relative
assertFalse(p.isAbsolute());
```

### Example (incorrect — missing "C:" edge case):
```java
// MISSING the "C:" → false case
Path p = new Path("C:/my/windows/path");
assertTrue(p.isAbsolute());

p = new Path("b:\\my\\abs\\windows\\path");
assertTrue(p.isAbsolute());

// Never tested "C:" which would have caught the regression!
```