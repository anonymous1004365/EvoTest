---
name: url-encoder-apostrophe-encoding
description: When testing URL path encoding using UrlEncoder.PATH_INSTANCE (Apache
  Wicket), the apostrophe character (') must be percent-encoded as %27. A common bug
  is failing to encode apostrophes in path segments, which later get XML-encoded and
  break JavaScript URLs. This skill teaches how to test that all three UrlEncoder
  types (QUERY, PATH, HEADER) handle apostrophes according to their respective encoding
  rules.
code_tags:
- CHARACTER_ENCODING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# url-encoder-apostrophe-encoding

## Instructions

# URL Encoder Apostrophe Encoding Test

## Instructions

WHEN testing the `UrlEncoder` class (from `org.apache.wicket.util.encoding`) and its three static instances `QUERY_INSTANCE`, `PATH_INSTANCE`, and `HEADER_INSTANCE`:

- THEN verify that `UrlEncoder.PATH_INSTANCE.encode("someone's bad url", "UTF-8")` returns `"someone%27s%20bad%20url"`. The apostrophe `'` (U+0027) must be encoded as `%27` in the PATH encoder.
- ALSO verify that `UrlEncoder.QUERY_INSTANCE.encode("someone's bad url", "UTF-8")` returns `"someone%27s+bad+url"`. Apostrophes are encoded in QUERY mode too, but spaces become `+` instead of `%20`.
- ALSO verify that `UrlEncoder.HEADER_INSTANCE.encode("someone's bad url", "UTF-8")` returns `"someone%27s%20bad%20url"`. Apostrophes and spaces are both encoded in HEADER mode.

WHEN the `encodeApostrophe` test (WICKET-3721) fails:
- THEN the expected failure is that the PATH encoder returns `"someone's%20bad%20url"` (leaving the apostrophe unencoded) instead of the correct `"someone%27s%20bad%20url"`.
- THEN verify that the `dontNeedEncoding` BitSet in the `UrlEncoder(Type.PATH)` constructor does NOT includes `'\''` (0x27). The apostrophe must NOT be in the set of characters that skip encoding for PATH mode.

Common pitfalls to avoid:
- **Testing only one encoder type**: The three instances (QUERY, PATH, HEADER) have different `dontNeedEncoding` sets. Always test all three or at minimum the one relevant to the bug.
- **Assuming apostrophe encoding is identical across encoders**: The QUERY encoder's comment says `"'\" doesn't need encoding`, but that comment is misleading — in the `switch (QUERY)` block, apostrophe is NOT added to `dontNeedEncoding`, which means it IS encoded. The comment only refers to JavaScript usability concerns.
- **Using `CharEncoding.UTF_8` vs `"UTF-8"`**: Both work, but be consistent. The test uses `org.apache.wicket.util.crypt.CharEncoding.UTF_8`.
- **Testing only `encodeApostrophe` in isolation**: The `pathUnencoded` test already loops over character candidates and checks that unexpected ones are encoded. When adding apostrophe, update both the `pathUnencoded` baseline string AND add a dedicated test like `encodeApostrophe`.

### Correct test example:
```java
@Test
public void encodeApostrophe()
{
    assertEquals("someone%27s%20bad%20url",
        UrlEncoder.PATH_INSTANCE.encode("someone's bad url", CharEncoding.UTF_8));
}
```

### Incorrect test that would NOT catch the bug:
```java
// This only checks the QUERY encoder and misses the PATH bug
@Test
public void testApostropheQuery()
{
    assertEquals("someone%27s+bad+url",
        UrlEncoder.QUERY_INSTANCE.encode("someone's bad url", CharEncoding.UTF_8));
}
```