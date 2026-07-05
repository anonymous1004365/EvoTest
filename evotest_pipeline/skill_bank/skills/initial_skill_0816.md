---
name: url-decoded-file-path-validation
description: When testing methods that convert URLs to local file paths, validate
  that spaces and special characters are correctly decoded rather than left as percent-encoded.
  This skill applies to any method using URL-to-File conversion where the URL path
  contains encoded characters.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# url-decoded-file-path-validation

## Instructions

# URL-Decoded File Path Validation

## Instructions

- WHEN the TG encounters a method that converts a URL (string or URL object) to a local file path — such as `Files.getLocalFileFromUrl(String)` or `Files.getLocalFileFromUrl(URL)` — and the URL may contain percent-encoded characters (e.g., `%20` for space)
- THEN the TG should write a test that provides a URL with percent-encoded special characters and verify the returned `File` object has a path with the decoded (unescaped) characters. For example, `file:/path/to/file%20with%20whitespace.txt` should produce a `File` whose `getPath()` or `toString()` equals `/path/to/file with whitespace.txt` (not `file%20with%20whitespace.txt`).
- Concrete example: For the method `Files.getLocalFileFromUrl(String url)`, test with `url = "file:/path/to/file with whitespace.txt"` and verify `file.toString().contains(" with ")` and does NOT contain `%20`. Also test with a `URL` object created from a percent-encoded string like `new URL("file:/path/file%20name.txt")`.
- Common pitfalls:
  - Testing only with URLs that contain no special characters (e.g., only alphanumeric paths) — this will not detect the decoding bug.
  - Asserting the entire path string literally (e.g., `assertEquals("/path/to/file name.txt", file.getPath())`) without accounting for OS path differences (e.g., Windows backslashes). Instead, use `assertTrue(file.getPath().contains(" with "))` or `assertTrue(file.getPath().contains(" "))`.
  - Forgetting to test the `URL` overload in addition to the `String` overload — both may be affected.
  - Assuming that if the method doesn't throw an exception, the conversion is correct — the bug manifests as incorrect (still percent-encoded) output, not a crash.
- Correct example:
  ```java
  @Test
  public void fileWithWhitespace()
  {
      String url = "file:/path/to/file with whitespace.txt";
      File file = Files.getLocalFileFromUrl(url);
      // verify space is decoded, not left as %20
      assertTrue("Path should contain decoded space", file.toString().contains(" with "));
      assertFalse("Path should not contain percent-encoded space", file.toString().contains("%20"));
  }
  ```
- Incorrect example:
  ```java
  @Test
  public void testGetLocalFileFromUrl()
  {
      // BAD: URL with no special characters — will not detect the bug
      String url = "file:/path/to/file.txt";
      File file = Files.getLocalFileFromUrl(url);
      assertNotNull(file);
      // This test passes even on the buggy version, so it's useless for catching the bug.
  }
  ```