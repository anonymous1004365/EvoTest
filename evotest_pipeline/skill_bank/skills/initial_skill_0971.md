---
name: url-path-decoding-conditionally-on-file-existence
description: Use when testing URL path extraction methods that decode percent-encoded
  or plus-encoded characters. Tests should verify that URLs referencing existing files
  are NOT decoded, while URLs referencing non-existing files ARE decoded.
code_tags:
- URI_RESOURCE_PATH_DECODING
test_pattern: PARAMETRIC_TEST
---

# url-path-decoding-conditionally-on-file-existence

## Instructions

# Conditional URL Path Decoding Based on File Existence

## Instructions

- WHEN the TG encounters a method that extracts a path from a `java.net.URL` (e.g. `ResolverUtil.extractPath(URL)`) and the method uses `URLDecoder.decode()` to decode percent/plus-encoded characters
- THEN the TG should test that the decoding behavior is conditional on whether the file referenced by the URL actually exists on the filesystem:
  - For URLs that point to an **existing file** on disk whose name contains `+` characters or percent-encoded characters (e.g. `file:/path/log4j+config+with+plus+characters.xml`), the extracted path should be returned **without decoding** (the `+` signs must remain as literal `+` characters, not converted to spaces)
  - For URLs that point to a **non-existing file** on disk (e.g. `file:///path+with+plus/file+does+not+exist.xml`), the extracted path should be **decoded** (the `+` signs should be converted to spaces)
- The TG should use `assertTrue(actual.endsWith(existingFile))` with an assertion message like `"should not be decoded: " + actual` for the existing-file case, and `assertEquals(expected, actual)` for the non-existing-file case
- A common pitfall: testing only with non-existing files (where decoding always applies) and missing the conditional behavior. The bug is that the method decodes the path even when the file exists, which breaks file resolution for real files with `+` in their names.
- Another pitfall: using `assertEquals()` for the existing-file case without checking via `endsWith()` — the test needs to compare against the full path which includes platform-specific directory prefixes that cannot be hardcoded

### Correct Test Pattern (existing file — must not decode):
```java
// Test: existing file with plus characters must NOT be decoded
final URL url = ResolverUtilTest.class.getResource("/log4j+config+with+plus+characters.xml");
final String actual = new ResolverUtil().extractPath(url);
assertTrue("should not be decoded: " + actual, actual.endsWith("/log4j+config+with+plus+characters.xml"));
```

### Correct Test Pattern (non-existing file — should decode):
```java
// Test: non-existing file with plus characters SHOULD be decoded
final URL url = new URL("file:///path+with+plus/file+does+not+exist.xml");
final String expected = "/path with plus/file does not exist.xml";
assertEquals(expected, new ResolverUtil().extractPath(url));
```

### Correct Test Pattern (jar URL with existing file — must not decode):
```java
// Test: existing file in jar URL with plus characters must NOT be decoded
URL url = ResolverUtilTest.class.getResource("/log4j+config+with+plus+characters.xml");
if (!url.getProtocol().equals("jar")) {
    url = new URL("jar:" + url.toExternalForm() + "!/some/entry");
}
final String actual = new ResolverUtil().extractPath(url);
assertTrue("should not be decoded: " + actual, actual.endsWith("/log4j+config+with+plus+characters.xml"));
```

### Correct Test Pattern (jar URL with non-existing file — should decode):
```java
// Test: non-existing file in jar URL with plus characters SHOULD be decoded
final URL url = new URL("jar:file:/path+with+plus/file+does+not+exist.jar!/some/file");
final String expected = "/path with plus/file does not exist.jar";
assertEquals(expected, new ResolverUtil().extractPath(url));
```

### Correct Test Pattern (URL with spaces AND plus characters in name — must not decode):
```java
// Test: existing file with spaces and plus characters must NOT be decoded
final String existingFile = "/s p a c e s/log4j+config+with+plus+characters.xml";
URL url = ResolverUtilTest.class.getResource(existingFile);
if (!url.getProtocol().equals("jar")) {
    url = new URL("jar:" + url.toExternalForm() + "!/some/entry");
}
final String actual = new ResolverUtil().extractPath(url);
assertTrue("should not be decoded: " + actual, actual.endsWith(existingFile));
```

### Incorrect Pattern (missing conditional behavior):
```java
// WRONG: always tests with non-existing files, never checks real files
final URL url = new URL("file:///some+path/file+name.xml");
assertEquals("/some path/file name.xml", new ResolverUtil().extractPath(url)); // only tests decode path
```

### Incorrect Pattern (hardcoding the full path for existing file):
```java
// WRONG: the full path is platform-specific, cannot be hardcoded
final URL url = ResolverUtilTest.class.getResource("/log4j+config+with+plus+characters.xml");
assertEquals("/home/user/project/log4j config with plus characters.xml", new ResolverUtil().extractPath(url)); // platform-dependent
```