---
name: absolute-url-parsing-robustness
description: When parsing URL strings into protocol/host/port/path components, the
  TG should test with unusual but valid URL formats (e.g., missing trailing slash,
  unusual port numbers) to detect parsing bugs. This skill helps write tests that
  catch URL parsing logic that incorrectly rejects or mangles valid absolute URLs.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# absolute-url-parsing-robustness

## Instructions

# Absolute URL Parsing Robustness

## Instructions

- WHEN the TG encounters code that parses URL strings and constructs `Url` objects (particularly through methods like `parseAbsoluteUrl()` or similar `Url.parse()` variants)
- THEN it should write a parametric test that exercises the URL parser with a variety of absolute URL formats to ensure all valid formats are correctly parsed. Specifically:
  - **Test with absolute URLs that have a trailing slash BEFORE the path**: e.g., `http://localhost:8080/foo` (port followed by `/path`). This is a standard valid URL format that must parse correctly.
  - **Test with absolute URLs that have NO trailing slash before the path**: e.g., `http://localhost:8080foo` (port immediately followed by path characters without a separator `/`). Depending on URL specification compliance, this may or may not be valid — the test should verify the parser's behavior is consistent and does not throw unexpected exceptions.
  - **Test with edge-case port values**: e.g., port `0`, port `65535`, very large port numbers, or URLs without a port.
  - **Test that the parsed `Url` object's components (protocol, host, port, path segments) are correct**: Verify `getProtocol()`, `getHost()`, `getPort()`, and the path segments via iteration.
  - **Expect an exception or specific behavior** (not a silent failure/crash) when the input is truly malformed.

- Common pitfalls to avoid:
  - **Testing only one or two URL formats**: The parser might handle common forms like `http://host/path` but fail on `http://host:8080/path` or `http://host:8080path`.
  - **Testing only protocol+host without port**: Port parsing is a common source of bugs — always include port variants.
  - **Assuming the parser follows RFC 3986 strictly**: Many parsers have quirks; the test should document the actual expected behavior.
  - **Not verifying the parsed components individually**: A test that only checks that parsing didn't throw is weak; asserting `getHost()`, `getPort()`, etc. is stronger.
  - **Not testing both with and without trailing slash**: Some parsers treat `http://host:8080/` differently from `http://host:8080`.

### Correct Example (JUnit 5 style):
```java
@ParameterizedTest
@CsvSource({
    "http://localhost:8080/foo, localhost, 8080, foo",
    "http://localhost/foo, localhost, -1, foo",
    "http://localhost:8080foo, localhost, 8080, foo",
    "http://localhost:0/bar, localhost, 0, bar",
})
void parseAbsoluteUrl_VariousFormats(String urlStr, String expectedHost, int expectedPort, String expectedFirstSegment) {
    Url url = Url.parse(urlStr);
    assertThat(url.getHost()).isEqualTo(expectedHost);
    assertThat(url.getPort()).isEqualTo(expectedPort);
    assertThat(url.getSegments()).isNotEmpty();
    assertThat(url.getSegments().get(0)).isEqualTo(expectedFirstSegment);
}
```

### Incorrect Example (weak testing):
```java
@Test
void parseAbsoluteUrl_Basic() {
    // Only tests one format, no port, no edge cases
    Url url = Url.parse("http://example.com/path");
    assertNotNull(url);
    // Does not verify any parsed components individually
}
```