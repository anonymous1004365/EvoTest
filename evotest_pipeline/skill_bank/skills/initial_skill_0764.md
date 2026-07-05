---
name: service-url-constructor-path-encoding
description: When constructing service URLs from server names that contain both schema
  (http/https) and path components, test that the URL is constructed correctly without
  double-encoding or malformation. This skill applies to URL/URI construction methods
  for CAS client utility code.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# service-url-constructor-path-encoding

## Instructions

# Service URL Construction with Server Name Containing Path and Schema

## Instructions

- WHEN the TG encounters a method that constructs a service URL by parsing a `serverName` parameter that may include both a scheme (e.g., `http://`, `https://`) and a path component (e.g., `localhost:8080/cas`)
- THEN the TG should write a parametric test that:
  1. Passes a server name containing both scheme AND path (e.g., `"https://server.example.com/app"`) along with a `service` parameter and request parameters
  2. Verifies that the resulting service URL is well-formed with the scheme, host, and path correctly preserved
  3. Tests that the URL does NOT double-encode or duplicate path segments (e.g., the path `/app` should appear exactly once)
  4. Verifies the URL correctly appends query parameters when provided
  5. Uses `assertTrue(serviceUrl.startsWith("https://server.example.com/app"))` to verify the correct prefix
  6. Passes values like `"https://server.example.com/app"` as the serverName and `"https://server.example.com/app?param=value"` or similar as the expected output

- Common pitfalls the TG might fall into:
  - Testing only server names without a path component, which would miss the path-encoding bug
  - Testing only server names without a scheme prefix, which would miss the scheme-preservation issue
  - Assuming the method always returns a value equal to the passed service parameter without considering the serverName parsing logic
  - Not testing URL construction with BOTH scheme and path present simultaneously

- Correct example:
```java
@Test
public void testConstructServiceUrlWithServerNameContainingPathAndSchema() {
    // serverName includes both scheme and path
    String serverName = "https://server.example.com/app";
    // The service URL should be properly constructed with the path preserved
    String serviceUrl = CommonUtils.constructServiceUrl(serverName, null, null);
    assertTrue(serviceUrl.startsWith("https://server.example.com/app"));
}
```

- Incorrect example (would NOT catch this bug):
```java
@Test
public void testConstructServiceUrl() {
    // Only testing a simple serverName without path or scheme
    String serverName = "localhost:8080";
    String serviceUrl = CommonUtils.constructServiceUrl(serverName, null, null);
    // This test passes even with the bug because no path/scheme interaction exists
    assertNotNull(serviceUrl);
}
```