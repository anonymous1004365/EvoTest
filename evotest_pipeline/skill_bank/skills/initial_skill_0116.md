---
name: bookmarkable-page-non-ascii-class-url-encoding
description: ''
code_tags:
- ENCODING_ESCAPING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# bookmarkable-page-non-ascii-class-url-encoding

## Instructions

# Bookmarkable Page URL Encoding with Non-ASCII Class Names

## Instructions

- WHEN the TG encounters a method that encodes a bookmarkable page URL (e.g., in `AbstractWebRequestCodingStrategy`, `BookmarkableMapper`, `MountedMapper`, or any class implementing `IRequestCodingStrategy` or `IRequestMapper` that produces URLs for bookmarkable pages)
  - THEN the TG should write a test that passes a page class whose **fully qualified class name** contains **non-ASCII characters** (e.g., `ÜberPage`, `MüllerPage`, `Página`, `Pageñol`) and verify that the URL produced by `encode(...)` or `urlFor(...)` correctly encodes those characters.
  - The test should verify that the URL path contains the **URL-encoded** form (percent-encoded) of the non-ASCII class name, e.g., `%C3%9CberPage` for `ÜberPage` instead of the raw `ÜberPage`.
  - Expect that on the buggy version the URL will contain **raw/unencoded non-ASCII characters**, which may cause the test to fail or the URL to be invalid. Verify by checking that the URL string does NOT contain raw non-ASCII bytes or that the encoded path segment is properly percent-encoded.

- WHEN the TG encounters a method that encodes page class names into URL path segments (e.g., `encodePageClass`, `encodePage`, `getPathForPage`, or similar)
  - THEN the TG should test with **at least 3 different non-ASCII characters**: a character from Latin-1 Supplement (e.g., `ü` → `%FC` or `%C3%BC`), a character from Cyrillic (e.g., `Ф` → `%D0%A4`), and a character with combining marks (e.g., `é` → `%C3%A9`).
  - Common pitfall: testing only with ASCII class names or only with a single non-ASCII character. Non-ASCII characters can span 1-4 bytes in UTF-8 and the encoding logic might handle only single-byte encodings or fail entirely for multi-byte sequences.
  - The test should use `org.junit.Assert.assertEquals` or `Assert.assertThat` with `CoreMatchers.containsString` to verify proper percent-encoding and should also verify that calling `Url.parse(encodedUrl)` round-trips correctly (i.e., the decoded URL reconstructs the original non-ASCII string).

- WHEN the TG is testing bookmarkable page URL encoding and the framework internally uses `java.net.URLEncoder` or `java.net.URI` for path encoding
  - THEN the TG should also test with page class names that contain **reserved URI characters** (e.g., spaces, `/`, `%`, `+`) in combination with non-ASCII characters, as these can interact badly with simplistic encoding approaches that only handle special characters but skip non-ASCII.
  - Common pitfall: assuming that URL encoding of non-ASCII characters is handled by a downstream library call. Many custom encoding routines fail to encode non-ASCII characters because they only check for characters < 0x20 or > 0x7E incorrectly, or use `String.getBytes()` with the platform default charset instead of UTF-8.

## Correct Example

```java
@Test
public void testEncode__bookmarkablePage_nonAsciiClassNames() {
    // Define a page class with non-ASCII characters in its name
    // (e.g., using anonymous inner class or a helper with ü, ñ, é)
    Class<? extends Page> nonAsciiPageClass = new Page() {}.getClass() {
        // just use the anonymous class name which contains non-ASCII
    };
    
    // Or use a statically defined page with non-ASCII name (e.g., "ÜberPage")
    // Create a request handler for the bookmarkable page
    PageParameters parameters = new PageParameters();
    IRequestHandler handler = new BookmarkablePageRequestHandler(
        new PageComponentInfo(null, null, null, null),
        ÜberPage.class, parameters);
    
    Url url = codingStrategy.encode(handler);
    
    // Verify that non-ASCII characters are percent-encoded in the URL path
    String encodedUrl = url.toString();
    assertThat("Non-ASCII class name should be percent-encoded",
        encodedUrl, not(containsString("ÜberPage")));
    assertThat("Non-ASCII class name should be percent-encoded",
        encodedUrl, containsString("%C3%9CberPage"));
}
```

## Incorrect Example

```java
@Test
public void testEncode__bookmarkablePage() {
    // Only testing ASCII class names — this would NOT catch the non-ASCII encoding bug
    IRequestHandler handler = new BookmarkablePageRequestHandler(
        new PageComponentInfo(null, null, null, null),
        HomePage.class, new PageParameters());
    
    Url url = codingStrategy.encode(handler);
    
    // Only checks that no exception is thrown and URL is not null
    assertNotNull(url);
}
```

The incorrect example fails to test with non-ASCII class names, so it would not detect the encoding bug.