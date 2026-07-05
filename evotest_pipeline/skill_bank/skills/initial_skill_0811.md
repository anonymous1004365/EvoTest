---
name: jcr-path-syntax-validation
description: When testing methods that convert or validate JCR path strings (like
  getOakPath or JcrPathParser), include paths containing control characters, unicode
  surrogates, and structural edge-cases beyond just common invalid patterns like double-slashes
  or invalid namespaces. These can bypass early-exit optimizations like needsFullMapping
  and expose latent parsing bugs.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# jcr-path-syntax-validation

## Instructions

# JCR Path Syntax Validation

## Instructions

- WHEN the TG encounters a method that parses or validates JCR paths (such as `NamePathMapperImpl.getOakPath(String jcrPath)` or `JcrPathParser.parse(...)`)
- THEN the TG should test with a comprehensive set of invalid JCR path strings that go beyond the typical "double slash" or "invalid namespace prefix" patterns. Include paths containing:
  - **Control characters**: e.g. `"foo\tbar"`, `"foo\nbar"`, `"foo\u0000bar"` (tab, newline, null character)
  - **Unicode surrogates**: e.g. `"foo\uD800bar"`, `"foo\uDC00bar"` (lone high/low surrogates)
  - **Structural edge-cases**: e.g. paths with trailing characters after an identifier bracket like `"[uuid]abc"` (should return `null` from `getOakPath`), paths with embedded null characters, empty segments, or invalid index notations like `"foo[0]"` or `"foo[-1]"`
- The test should verify that `npMapper.getOakPath(invalidPath)` returns `null` for each invalid JCR path, or that `JcrPathParser.validate(invalidPath)` returns `false`
- Common pitfalls:
  - Testing only syntactically invalid paths like `"//"`, `"/.."`, or `"foo::bar"` while missing paths with control characters or unicode surrogates that the JCR spec also considers invalid
  - Assuming the `needsFullMapping` fast-path correctly rejects all invalid inputs — the fast-path only checks for `{`, `[`, `.`, `:`, and `/` as first characters, so paths starting with regular characters but containing control characters deeper in the string bypass the initial validation

### Example (Correct)
```java
@Test
public void testInvalidJcrPathsExtended() {
    String[] invalidPaths = {
        "//",
        "/foo//",
        "/..//",
        "/..",
        "/foo/../..",
        "foo::bar",
        "foo:bar:baz",
        "foo:bar]baz",
        "foo:bar[baz",
        "foo:bar|baz",
        "foo:bar*baz",
        "foo\tbar",           // control character (tab)
        "foo\nbar",           // control character (newline)
        "foo\u0000bar",       // null character
        "foo\uD800bar",       // lone high surrogate
        "foo\uDC00bar",       // lone low surrogate
        "foo[0]",             // invalid index (0)
        "foo[-1]"             // invalid index (negative)
    };
    
    for (String path : invalidPaths) {
        assertNull("Expected null for invalid path: " + path, 
            npMapper.getOakPath(path));
    }
}
```

### Example (Incorrect)
```java
@Test
public void testInvalidJcrPaths() {
    // Only the basic invalid patterns — misses control chars, surrogates, etc.
    String[] paths = {"//", "/..", "foo::bar"};
    for (String path : paths) {
        assertNull(mapper.getOakPath(path));
    }
}
```