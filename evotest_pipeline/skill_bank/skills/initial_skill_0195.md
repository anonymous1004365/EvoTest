---
name: page-class-non-ascii-url-encoding
description: When encoding URLs for bookmarkable pages with class names containing
  non-ASCII characters, the test must verify both the URL encoding/decoding round-trip
  and that the class name survives the encode/decode cycle without corruption. This
  skill is triggered when testing URL encoding strategies that handle page class names.
code_tags:
- URL_ENCODING_NON_ASCII
- PAGE_CLASS_LOADING
test_pattern: PARAMETRIC_TEST
---

# page-class-non-ascii-url-encoding

## Instructions

# Bookmarkable Page URL Encoding with Non-ASCII Class Names

## Instructions

### WHEN the TG encounters a URL encoding strategy (e.g., `WebRequestCodingStrategy`, `CryptedUrlWebRequestCodingStrategy`) that encodes bookmarkable page URLs:

- **THEN** the TG MUST write a test that passes a page class whose fully qualified name contains non-ASCII characters (e.g., accented letters like `é`, `ü`, `ñ`, or CJK characters) and verify the full round-trip: encode → decode → class resolution.

- **THEN** the test MUST verify that after encoding a bookmarkable page URL:
  1. The encoded URL decodes back to the same class name without data loss
  2. The decoded class can be resolved/loaded via class loading mechanisms
  3. A `ClassNotFoundException` or `ClassCastException` is NOT thrown when the decoded class name is used to load the page class

- **THEN** the TG MUST use a specific non-ASCII page class name pattern, such as:
  - A class with accented characters in the package name (e.g., `org.apache.wicket.protocol.http.request.écoledirecte.PageAccueil`)
  - Or use string manipulation to create the class name with Unicode characters at test time

- **WHEN** testing `encodeBookmarkablePage` or `urlFor(IRequestHandler)` methods that accept `PageParameters`:
  - **THEN** test with a `PageParameters` map that contains string values with non-ASCII characters
  - **THEN** verify the full request cycle: creating a `BookmarkablePageRequestHandler`, encoding to `CharSequence`, decoding back to `IRequestHandler`, and comparing the original page class with the decoded one

- **COMMON PITFALLS TO AVOID:**
  - Testing only ASCII-only class names — this masks URL encoding bugs
  - Testing only URL encoding without testing URL decoding and class name reconstruction
  - Assuming UTF-8 encoding is correctly applied to class names (may use system default charset)
  - Testing parameter values but not the page class name itself

### Example (Correct):

```java
@Test
public void testEncode_bookmarkablePage_nonAsciiClassNames() throws Exception
{
    // Create a page class reference with non-ASCII characters
    // Ensure the class exists or use a mock that represents such a class
    Class<?> pageClass = HomePage.class; // ASCII fallback; use actual non-ASCII class if available
    
    // Or more robustly:
    String className = "org.apache.wicket.protocol.http.request.écoledirecte.PageAccueil";
    
    // Test that the URL encoding strategy properly encodes and decodes the class name
    CryptedUrlWebRequestCodingStrategy strategy = new CryptedUrlWebRequestCodingStrategy();
    RequestCycle requestCycle = ...;
    
    // Create a request handler for a bookmarkable page
    IRequestHandler handler = new BookmarkablePageRequestHandler(pageClass, new PageParameters());
    CharSequence url = strategy.encode(requestCycle, handler);
    
    // Decode back
    IRequestHandler decoded = strategy.decode((Request) url);
    
    // Verify the decoded handler references the same page class
    assertNotNull("Decoded handler should not be null", decoded);
    // Verify no data loss in the class name
}
```

### Example (Incorrect):

```java
// BAD: Only tests with ASCII page names, missing the non-ASCII bug
@Test
public void testEncode_bookmarkablePage()
{
    Class<?> pageClass = HomePage.class; // Only ASCII
    // ... test passes even though non-ASCII would fail
}

// BAD: Tests encoding but not the full round-trip decode
@Test
public void testEncode_bookmarkablePage_partial()
{
    // Encodes but never decodes to verify class name integrity
}
```