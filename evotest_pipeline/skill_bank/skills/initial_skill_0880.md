---
name: url-parsing-is-full-hint
description: When parsing URLs that may be absolute (protocol-less with "//" or scheme-based),
  always test with the `isFullHint` parameter set to `false` to verify that the URL
  is parsed as a relative/context-absolute URL rather than extracting host/protocol.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- NULL_CHECK
- ABSOLUTE_URL_RENDERING
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# url-parsing-is-full-hint

## Instructions

# URL Parsing with `isFullHint` Parameter

## Instructions

**WHEN** the code under test calls `Url.parse(CharSequence, Charset)` or `Url.parse(CharSequence, Charset, boolean)` — especially with a URL that starts with `//` (protocol-less absolute URL) — **THEN** the test must verify the behavior of the `isFullHint` parameter:

1. **Test `isFullHint=true` (the default):** WHEN parsing a `//host/path` URL with `isFullHint=true` or using the two-argument `parse()`, THEN verify that `url.getHost()` returns the host portion (e.g. `"host"`), `url.getProtocol()` is `null`, and the segments start after the host.

2. **Test `isFullHint=false`:** WHEN parsing the same `//host/path` URL with `isFullHint=false`, THEN verify that no host or protocol is extracted — the entire string is treated as relative URL segments. The first segment should be `""`, and subsequent segments should be `"host"`, `"path"`, etc.

3. **Additionally test a scheme-full URL** like `"http://host:12345/path"` with `isFullHint=false`: verify that no protocol/host/port is extracted and the entire URL is treated as segments.

**Common pitfalls to avoid:**
- Testing only with `isFullHint=true` (the default) and missing the `isFullHint=false` path entirely.
- Assuming that `parse(CharSequence)` and `parse(CharSequence, Charset)` always detect full URLs correctly — they use `isFullHint=true` by default, but callers may pass `false`.
- Forgetting that the `isFullHint` parameter was added specifically to suppress automatic detection of protocol/host/port.

### Examples:

**Correct test (catches the bug):**
```java
@Test
public void parseAbsoluteUrl_customIsFullHint()
{
    // With isFullHint = true (default behavior) - extracts host
    Url urlWithHint = Url.parse("//host/path", null, true);
    assertEquals("host", urlWithHint.getHost());
    assertNull(urlWithHint.getProtocol());
    assertEquals(Arrays.asList("", "path"), urlWithHint.getSegments());

    // With isFullHint = false - treats as relative URL
    Url urlWithoutHint = Url.parse("//host/path", null, false);
    assertNull(urlWithoutHint.getHost());
    assertNull(urlWithoutHint.getProtocol());
    assertEquals(Arrays.asList("", "host", "path"), urlWithoutHint.getSegments());

    // Also test scheme URL with isFullHint=false
    Url schemeUrl = Url.parse("http://host:12345/path", null, false);
    assertNull(schemeUrl.getHost());
    assertNull(schemeUrl.getProtocol());
    assertNull(schemeUrl.getPort());
}
```

**Incorrect test (misses the bug):**
```java
@Test
public void parseAbsoluteUrl()
{
    // Only tests default behavior, never passes isFullHint=false
    Url url = Url.parse("//host/path");
    assertEquals("host", url.getHost());
    
    Url url2 = Url.parse("http://host:12345/path");
    assertEquals("http", url2.getProtocol());
    assertEquals("host", url2.getHost());
    // Bug: the isFullHint=false path is never tested
}
```