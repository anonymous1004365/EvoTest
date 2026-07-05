---
name: ipv6-address-square-bracket-parsing
description: When parsing IPv6 addresses with square brackets in URL strings, test
  that the brackets are properly stripped before parsing the address. This skill helps
  detect NumberFormatException bugs caused by residual bracket characters in IPv6
  address segments.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# ipv6-address-square-bracket-parsing

## Instructions

# IPv6 Address Square Bracket Parsing

## Instructions

- WHEN the TG encounters code that parses IPv6 addresses from URLs containing square-bracketed segments (e.g. `"[::1]"` or `"[2001:db8::1]"`)
- THEN the TG should write tests that pass IPv6 address strings WITH brackets to the parsing method and verify the address is correctly extracted WITHOUT the brackets
  - For example, test that `Url.parse("http://[::1]:8080/path")` produces a URL with host `"::1"` (no brackets), not `"[::1]"` or throwing `NumberFormatException`
  - Test that `Url.parse("http://[2001:db8::1]/path")` succeeds and the parsed host is `"2001:db8::1"`
  - Test edge cases like `"http://[::1]"` (IPv6 localhost), `"http://[fe80::1%25eth0]"` (IPv6 with zone ID), and `"http://[::ffff:192.0.2.1]"` (IPv4-mapped IPv6)
- When a test calls a method that parses an IPv6 address from a bracketed URL segment, verify that the test expects the correct address string (without brackets) and that the parsing does NOT throw a `NumberFormatException` due to residual bracket characters like `"]"`
- Common pitfalls to avoid:
  - Testing only IPv4 addresses and forgetting IPv6 addresses with square brackets
  - Assuming the brackets are stripped by the caller rather than by the parsing method itself
  - Not testing the `NumberFormatException` scenario — the buggy version may throw `NumberFormatException: For input string: "1]"` when brackets leak through to `Integer.parseInt()` or similar numeric parsing
  - Testing only well-formed URLs and skipping bracket-terminated or bracket-containing edge cases

### Example (Correct Test)

```java
@Test
public void parseIp6Address()
{
    // IPv6 localhost with brackets — must not throw NumberFormatException
    Url url = Url.parse("http://[::1]:8080/path");
    assertEquals("::1", url.getHost());
    assertEquals(8080, url.getPort());
    
    // IPv6 with brackets, no port
    url = Url.parse("http://[2001:db8::1]/path");
    assertEquals("2001:db8::1", url.getHost());
    
    // IPv6 with zone ID
    url = Url.parse("http://[fe80::1%25eth0]/path");
    assertEquals("fe80::1%eth0", url.getHost());
    
    // IPv4-mapped IPv6
    url = Url.parse("http://[::ffff:192.0.2.1]/path");
    assertEquals("::ffff:192.0.2.1", url.getHost());
}
```

### Example (Incorrect Test — Does Not Catch the Bug)

```java
@Test
public void parseIp6Address()
{
    // Only testing IPv4 — misses the IPv6 bracket bug entirely
    Url url = Url.parse("http://127.0.0.1:8080/path");
    assertEquals("127.0.0.1", url.getHost());
    
    // Testing IPv6 WITHOUT brackets — not realistic for URL parsing
    // Real URLs always have brackets around IPv6 addresses
    Url url2 = Url.parse("http://::1/path");  // This is technically invalid
}
```