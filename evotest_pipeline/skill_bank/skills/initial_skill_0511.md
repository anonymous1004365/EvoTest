---
name: url-parsing-with-credentials
description: Teaches how to test URL parsing when user credentials (username:password@host)
  are present in the authority section. Use when validating that Url.parse() handles
  URLs containing '@' in the authority part (credentials) without crashing on port
  number parsing.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# url-parsing-with-credentials

## Instructions

# URL Parsing with User Credentials in Authority

## Instructions

- WHEN the TG encounters code that parses full URLs containing an `@` character in the authority section (e.g., `http://me:secret@localhost` or `http://user:pass@host:port/path`)
- THEN the TG should write a test that calls `Url.parse()` with a URL string containing credentials in the authority part. The test must verify that:
  1. Parsing `"http://me:secret@localhost"` succeeds without throwing `NumberFormatException` (the buggy version throws `NumberFormatException: For input string: "secret@localhost"`)
  2. `result.getHost()` returns `"me:secret@localhost"` (the entire authority after protocol is treated as host when there's no port)
  3. `result.getPort()` returns `null` when no explicit port is present
  4. Parsing `"http://me:secret@localhost:8080"` correctly extracts: protocol=`"http"`, host=`"me:secret@localhost"`, port=`Integer.valueOf(8080)`
  
- Common pitfalls to avoid:
  - Testing only the host part without credentials (`"http://localhost:8080"`) — this passes on the buggy version too
  - Testing only the port-containing variant without also testing the no-port variant
  - Assuming that `@` in a URL always separates credentials from host — the bug is that the code uses `lastIndexOf(':')` on the wrong substring, so when credentials contain `@` but no `:` exists after them, `portAt` is computed incorrectly and `Integer.parseInt()` is called on the credentials string
  - Not checking `getHost()` and `getPort()` independently

### Correct test example:
```java
@Test
public void parseUrlWithCredentials_NoPort()
{
    // WICKET-5259: URL with user:password@host but no port
    String s = "http://me:secret@localhost";
    Url url = Url.parse(s);
    assertEquals("http", url.getProtocol());
    assertEquals("me:secret@localhost", url.getHost());
    assertNull(url.getPort());
}

@Test
public void parseUrlWithCredentials_WithPort()
{
    // WICKET-5259: URL with user:password@host:port
    String s = "http://me:secret@localhost:8080";
    Url url = Url.parse(s);
    assertEquals("http", url.getProtocol());
    assertEquals("me:secret@localhost", url.getHost());
    assertEquals(Integer.valueOf(8080), url.getPort());
}
```

### Incorrect test example (would pass on buggy code too and miss the bug):
```java
@Test
public void parseNormalHostWithPort()
{
    // This only tests standard host:port without credentials - doesn't catch the bug
    String s = "http://localhost:8080";
    Url url = Url.parse(s);
    assertEquals("http", url.getProtocol());
    assertEquals("localhost", url.getHost());
    assertEquals(Integer.valueOf(8080), url.getPort());
}
```