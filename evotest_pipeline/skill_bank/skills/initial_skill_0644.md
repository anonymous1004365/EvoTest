---
name: path-unalignment-when-path-equals-basedir
description: When calling unalignFromBaseDirectory() with a path that exactly equals
  the basedir (no subdirectory), the method should return "." but may return an empty
  string or keep the original path due to missing edge case handling. Apply this skill
  whenever testing path-relative logic involving directory alignment/unalignment.
code_tags:
- BOUNDARY_CHECK
- PATH_NORMALIZATION
test_pattern: PARAMETRIC_TEST
---

# path-unalignment-when-path-equals-basedir

## Instructions

# Path Unalignment When Path Equals Basedir

## Instructions

- WHEN the TG encounters the `unalignFromBaseDirectory(String path, File basedir)` method that strips a basedir prefix from an absolute path to produce a relative path
- THEN the TG MUST write a test for the boundary case where `path` is **exactly equal** to `basedir.getAbsolutePath()` (i.e., the path IS the basedir, with no subdirectory). In this case, after stripping the basedir prefix, the remaining substring is empty (length 0). The method MUST replace the empty string with `"."` to represent the current directory. The TG should verify:
  1. Call `new DefaultPathTranslator().unalignFromBaseDirectory(basedir.getAbsolutePath(), basedir)`
  2. Assert that the result equals `"."`
  3. This test catches a bug where `path.length() <= 0` returns false for empty string because `path` was not reassigned after the `substring()` call, or the empty-check is missing entirely.
- The TG should ALSO test the general case where path is a subdirectory under basedir (e.g., `basedir.getAbsolutePath() + "/dir"`), and the result should be `"dir"` (a non-empty relative path).
- Common pitfalls:
  - Testing only subdirectory paths and never the exact-match boundary case
  - Assuming `path.substring(base.length())` will always produce a non-empty string
  - Forgetting that empty string `""` is semantically different from `"."` in path contexts
  - Using a hardcoded basedir path that doesn't match the runtime path (use `basedir.getAbsolutePath()` dynamically)

### Correct Example (catches the bug)
```java
public void testUnalignToBasedirWherePathEqualsBasedir()
{
    File basedir = new File( System.getProperty( "java.io.tmpdir" ), "test" ).getAbsoluteFile();
    String unaligned = new DefaultPathTranslator().unalignFromBaseDirectory( basedir.getAbsolutePath(), basedir );
    assertEquals( ".", unaligned );
}
```

### Incorrect Example (misses the bug)
```java
public void testUnalignToBasedir()
{
    File basedir = new File( System.getProperty( "java.io.tmpdir" ), "test" ).getAbsoluteFile();
    // Only tests a subdirectory path, never the exact-match boundary
    String unaligned = new DefaultPathTranslator().unalignFromBaseDirectory( new File(basedir, "dir").getAbsolutePath(), basedir );
    assertEquals( "dir", unaligned );
}
```