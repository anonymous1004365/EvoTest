---
name: uri-to-file-plus-character-handling
description: When converting URIs to File objects, URLDecoder.decode() converts '+'
  to spaces (application/x-www-form-urlencoded semantics), breaking filenames containing
  literal plus signs. The TG should test that filenames with '+' characters are preserved
  correctly.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# uri-to-file-plus-character-handling

## Instructions

# URI-to-File Conversion with Literal '+' Characters

## Instructions

- WHEN the TG encounters a method that converts a `java.net.URI` to a `java.io.File` by calling `uri.toURL().getFile()` and then passing the result through `URLDecoder.decode(fileName, charsetName)`
- THEN it should test with URIs containing literal `+` characters in filenames (not encoded as `%2B`) to verify they are NOT converted to spaces
- Specifically, when a URI like `target/test-classes/log4j+config+with+plus+characters.xml` (no scheme, or with `file:` scheme) is passed to the conversion method, the resulting `File.getName()` should return `"log4j+config+with+plus+characters.xml"` — NOT `"log4j config with plus characters.xml"`
- The bug occurs because `URLDecoder.decode()` treats `+` as a space character (per `application/x-www-form-urlencoded` spec), conflating URL encoding of query parameters with file path decoding
- Test both paths: (1) when the file EXISTS (the buggy code has a guard `new File(fileName).exists()` that returns early without decoding, which would work), AND (2) when the file DOES NOT EXIST (the early-return guard is bypassed, leading to incorrect decoding)
- **Common pitfall**: Testing only with files that exist on disk, which masks the bug because the early-exit path (`if (new File(fileName).exists()) return new File(fileName);`) skips the `URLDecoder.decode()` call entirely. The bug only manifests when decoding a non-existing file path with `+` characters — then `URLDecoder` converts `+` to spaces.

### Correct test approach (catches the bug):
```java
// Test with non-existing URI containing '+' characters
final String config = "NON-EXISTING-PATH/this+file+does+not+exist.xml";
final URI uri = new URI(config);
final File file = FileUtils.fileFromUri(uri);
// On buggy version: file.getName() == "this file does not exist.xml" (spaces)
// On fixed version:  file.getName() == "this+file+does+not+exist.xml" (plus signs preserved)
assertEquals("this+file+does+not+exist.xml", file.getName());
```

### Incorrect test approach (misses the bug):
```java
// Test ONLY with existing files - the bug won't manifest!
final String config = "target/test-classes/log4j+config+with+plus+characters.xml";
final URI uri = new URI(config);
// Buggy code takes the early return path because file exists, so '+' stays intact
// This test would pass on BOTH buggy and fixed versions, giving false confidence
final File file = FileUtils.fileFromUri(uri);
assertEquals("log4j+config+with+plus+characters.xml", file.getName());
```