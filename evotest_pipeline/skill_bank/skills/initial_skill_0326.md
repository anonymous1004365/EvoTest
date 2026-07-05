---
name: content-type-encoding-mutation
description: When constructing a content type string for a layout, the charset/encoding
  parameter must be explicitly appended after setting the base content type. Tests
  should verify that the content type header includes the charset parameter after
  calling getContentType(). This catches mutations where properties are set but the
  formatted output doesn't reflect them.
code_tags:
- VALIDATION
- STATE_MUTATION
- CONFIGURATION_RELOAD
test_pattern: STATE_TEST
---

# content-type-encoding-mutation

## Instructions

# Content Type Encoding Parameter Absence

## Instructions

- WHEN testing a layout class (such as `HtmlLayout`) that has a `contentType` or similar property, and the class's `getContentType()` method returns a MIME type string that SHOULD include a charset/encoding parameter (e.g., `"text/html; charset=UTF-8"` or `"text/html; charset=UTF-16"`):
  - THEN the TG should create a test that:
    1. Constructs a layout instance with a specific charset/encoding setting (e.g., using a builder or factory method)
    2. Calls `getContentType()` on the instance
    3. Asserts that the returned string contains the expected charset/encoding parameter using `assertEquals(expectedContentType, layout.getContentType())`
  - Because the bug is that setting the charset on the layout via a configuration property does NOT propagate into the content type string returned by `getContentType()` — the charset parameter is silently missing.

- WHEN testing content type output for `HtmlLayout`:
  - THEN test BOTH:
    - `"text/html; charset=UTF-8"` (default charset)
    - `"text/html; charset=UTF-16"` (non-default charset)
  - Because the failure in the buggy version is that `getContentType()` returns `"text/html"` without any charset parameter, regardless of what charset was configured.

- Common pitfalls to avoid:
  - **Testing only the base content type without charset**: The TG might test that the layout returns `"text/html"` and consider that sufficient. This misses the bug — the charset parameter is the key missing piece.
  - **Testing only the default charset**: The bug also manifests with non-default charsets (e.g., UTF-16). Test at least two different charset values to catch encoding-related state mutations.
  - **Using `contains` or `startsWith` instead of exact match**: The TG should use exact assertion (e.g., `assertEquals`) on the full expected content type string, not a substring match that could mask the missing parameter.

- Example of a correct test:
  ```java
  @Test
  public void testContentType() {
      // Test with default charset
      final HtmlLayout layout = HtmlLayout.createDefaultLayout();
      assertEquals("text/html; charset=UTF-8", layout.getContentType());

      // Test with non-default charset
      final HtmlLayout layoutUtf16 = HtmlLayout.newBuilder()
          .withCharset(StandardCharsets.UTF_16)
          .build();
      assertEquals("text/html; charset=UTF-16", layoutUtf16.getContentType());
  }
  ```

- Example of an incorrect test (that would NOT catch the bug):
  ```java
  @Test
  public void testContentTypeIncorrect() {
      final HtmlLayout layout = HtmlLayout.createDefaultLayout();
      // INCORRECT: This passes even on the buggy version because "text/html" is a substring
      assertTrue(layout.getContentType().contains("text/html"));
      // INCORRECT: This also passes on the buggy version
      assertEquals("text/html", layout.getContentType());
  }
  ```