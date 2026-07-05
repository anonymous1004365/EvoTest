---
name: layout-content-type-charset-inclusion
description: When a layout subclass overrides getContentType() and concatenates a
  charset string, verify the charset field is not null and is actually set before
  the content type is computed. The test should assert the full content type string
  to catch charset omission bugs.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# layout-content-type-charset-inclusion

## Instructions

# Layout Content-Type Charset Inclusion

## Instructions

WHEN the TG encounters a layout class that overrides `getContentType()` and returns a string that concatenates a charset (e.g., `return "text/xml; charset=" + this.getCharset()` or similar pattern), THEN the TG should write a test that:

1. Constructs the layout using its builder with an explicit charset (e.g., `StandardCharsets.UTF_8`).
2. Calls `layout.getContentType()` and asserts the full expected content-type string (e.g., `"text/xml; charset=UTF-8"`).

Specifically:
- The TG MUST assert the **complete string** returned by `getContentType()`, not just a substring prefix. For example, use `assertEquals("text/xml; charset=UTF-8", layout.getContentType())` rather than `assertTrue(layout.getContentType().startsWith("text/xml"))`.
- Be aware that `getContentType()` can return a value that references `this.getCharset()` or `this.charset`. If the charset field is not properly initialized (e.g., null, or the layout's constructor doesn't propagate the charset to the parent), the charset portion may be silently omitted.
- Verify that the charset portion (e.g., `"; charset=UTF-8"`) appears in the return value exactly as expected.
- When using a builder to construct the layout, ensure the builder sets the charset explicitly via `setCharset()` or equivalent.

**Common pitfalls to avoid:**
- Testing only the prefix (`"text/xml"`) — this passes even when the charset suffix is missing.
- Not setting the charset on the builder, relying on defaults that may or may not be propagated.
- Testing `getContentType()` in isolation without verifying the layout was fully constructed with all parameters.

### Correct Example (would catch the bug)

```java
@Test
public void testContentType() {
    final XmlLayout layout = XmlLayout.newBuilder()
        .setCharset(StandardCharsets.UTF_8)
        .build();
    assertEquals("text/xml; charset=UTF-8", layout.getContentType());
}
```

### Incorrect Example (would NOT catch the bug)

```java
@Test
public void testContentType() {
    final XmlLayout layout = XmlLayout.newBuilder().build();
    assertTrue(layout.getContentType().startsWith("text/xml"));
}
```