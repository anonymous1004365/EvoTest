---
name: url-port-parsing-with-path-parameters
description: When parsing URLs that have a port followed by a semicolon path parameter
  (e.g., http://host:56704;jsessionid=...), the TG should test that the port number
  is correctly extracted from the colon-separated section and that the semicolon-delimited
  content is handled as part of the path, not the port. This skill prevents NumberFormatException
  bugs where non-numeric port suffix data gets passed to Integer.parseInt.
code_tags:
- VALIDATION
- STRING_PARSING_COLON
test_pattern: EXCEPTION_TEST
---

# url-port-parsing-with-path-parameters

## Instructions

# URL Port Parsing with Path Parameters

## Instructions

- WHEN the TG encounters a URL parsing method that extracts a port number using `Integer.parseInt()` on a substring derived from `indexOf(':')` (e.g., `hostAndPort.substring(portOffset + 1)`)
- THEN the TG MUST verify that the parser correctly handles URLs where the port number is followed by a semicolon-delimited path parameter (such as `;jsessionid=...` or `;otherparam=value`). Specifically:
  - Parse a URL string like `"http://hostname:56704;jsessionid=8kxeo3reannw1qjtxgkju8yiu"` using `Url.parse()`
  - Assert that `url.getPort()` returns `Integer.valueOf(56704)` (NOT a NumberFormatException)
  - Assert that the path segments include the `;jsessionid=...` portion as a segment
- WHEN the TG encounters the `indexOf(':')` call used to locate the port separator, note that the `indexOf` is called on a substring that starts *after* any credentials (`@`) and closing square bracket (`]`). The `portAt` variable represents the colon index *relative to* that substring, and `portOffset` is computed as `portAt + credentialsAt + closeSqrBracketAt`.
- Common pitfalls to avoid:
  - **Testing only URLs without semicolon path parameters**: The bug only manifests when the port number is immediately followed by `;...` with no slash. A test like `"http://hostname:8080/foo"` alone will NOT catch this bug.
  - **Assuming the port section ends at the next `/` or end-of-string**: The buggy code uses `indexOf(':')` followed by `Integer.parseInt()` on everything after the colon up to the next `/` or end-of-string, but semicolons are not considered delimiters for the port number.
  - **Forgetting to test both protocol-prefixed URLs and protocol-less full URLs**: Test both `"http://hostname:56704;jsessionid=abc"` and `"//hostname:56704;jsessionid=abc"` forms.

### Correct test example (catches the bug):
```java
@Test
public void testParseUrlWithJSessionIdAfterPort()
{
    String s = "http://localhost:56704;jsessionid=8kxeo3reannw1qjtxgkju8yiu";
    Url url = Url.parse(s);
    assertEquals(Integer.valueOf(56704), url.getPort());
    checkSegments(url, ";jsessionid=8kxeo3reannw1qjtxgkju8yiu");
}
```

### Incorrect test (does NOT catch the bug):
```java
@Test
public void testParseUrlWithPort()
{
    String s = "http://localhost:56704/foo";
    Url url = Url.parse(s);
    assertEquals(Integer.valueOf(56704), url.getPort());
    // This test passes even on the buggy version, missing the bug entirely.
}
```