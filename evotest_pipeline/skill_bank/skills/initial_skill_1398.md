---
name: file-writing-charset-mismatch
description: When writing file content with an explicit charset, the TG should verify
  that the file writer uses the configured charset for content bytes. Without a charset-based
  write, the JVM default encoding may produce different byte sizes than expected,
  causing failures in cross-platform or charset-sensitive tests.
code_tags:
- CHARSET_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# file-writing-charset-mismatch

## Instructions

# File Writing Charset Mismatch

## Instructions

- WHEN the TG encounters a file component endpoint that configures a charset (e.g., `UTF-8` to `ISO-8859-1` transformation via `&charset=ISO-8859-1`)
- THEN the TG should write a test that sends a message containing non-ASCII characters (e.g., characters like `Æ`, `Ø`, `à`, `é`) through the route and asserts the size of the written file in bytes
  - For example, the string `"æøå\naøå\n"` encoded in UTF-8 is 12 bytes but in ISO-8859-1 is 9 bytes
  - Concrete: create a route `from("direct:start").to("file:target/charset?charset=ISO-8859-1")`, send a body with non-ASCII characters, verify the output file byte count matches the charset-specific size
- WHEN testing file output with charset conversion, verify that the written file's byte count corresponds to the **configured** charset, **not** the JVM default or UTF-8 encoding
  - Common pitfall: testing only with ASCII characters — ASCII characters encode identically across UTF-8 and ISO-8859-1, so such a test would not catch this bug
- WHEN asserting file content length, use `length()` on the `File` object or use a `String.getBytes("configured-charset").length` calculation to determine the expected size
- MISTAKE TO AVOID: Do not assume the body string length equals the file byte count — this is only true for single-byte charsets and ASCII content. Always calculate expected bytes using the configured charset.

### Correct Example (would catch the bug):
```java
String body = "æøå\naøå\n";
template.sendBody("direct:start", body);
File file = new File("target/charset/input.txt");
long expected = body.getBytes("ISO-8859-1").length; // 9 bytes
assertEquals(expected, file.length());
```

### Incorrect Example (would miss the bug):
```java
String body = "Hello World"; // only ASCII characters
template.sendBody("direct:start", body);
File file = new File("target/charset/input.txt");
// Both UTF-8 and ISO-8859-1 encode ASCII the same way, so this passes regardless
assertEquals(body.length(), file.length());
```