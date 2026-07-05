---
name: endpoint-uri-ampersand-parameter-masking
description: When resolving Camel endpoint URIs that contain a file path, the `&`
  character in the path must not be interpreted as a URI parameter separator. Test
  both literal paths with `&` and paths followed by actual URI parameters to verify
  correct parsing.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# endpoint-uri-ampersand-parameter-masking

## Instructions

# Endpoint URI Ampersand Parameter Masking

## Instructions

- WHEN the TG encounters code that constructs or resolves a Camel endpoint URI where the URI path component (e.g., `file:` path, `http:` path) could contain an ampersand (`&`) character
- THEN the TG should write a test that:
  1. Creates a file endpoint URI with a path containing `&` (e.g., `file://target/data/my%20file&stuff?noop=true`, `file://target/data/foo_&_bar.txt?move=done`, or any similar path with `&` before the query string) **and** includes actual URI query parameters after a `?`
  2. Attempts to resolve the endpoint via `context.getEndpoint(uri)` or `context.resolveEndpoint(uri)`
  3. Asserts that no `ResolveEndpointFailedException` is thrown — the URI must be parsed successfully
  4. Optionally asserts the resulting endpoint has the correct path (e.g., the path ends with the expected file path containing `&`) and that the query parameters (e.g., `noop=true`, `move=done`) are correctly applied

- WHEN the test is run against the **fixed** version, it must pass (the endpoint is resolved correctly)
- WHEN the test is run against the **buggy** version, it must fail (the endpoint resolution throws a `ResolveEndpointFailedException` because the `&` is incorrectly interpreted as a parameter separator)

- **Common pitfalls to avoid**:
  - Testing only with `&` in the URI and **no** query parameters (e.g., `file://target/data/my%20file&stuff` without `?noop=true`). This does not trigger the bug because there is no ambiguous `&`-as-separator scenario.
  - Testing only with query parameters and no `&` in the path.
  - Forgetting to URL-encode spaces or other special characters in the path — the key is that `&` appears in the path **before** the `?` query string.

- **Correct example** (triggers the bug):
```java
public void testPathWithAmpersand() throws Exception {
    FileEndpoint endpoint = context.getEndpoint(
        "file://target/data/Darjeeling & Jalpaiguri?noop=true", FileEndpoint.class);
    // On buggy version: throws ResolveEndpointFailedException
    // On fixed version: resolves successfully
    assertNotNull(endpoint);
    assertTrue(endpoint.getFile().toString().contains("&"));
}
```

- **Incorrect example** (does NOT trigger the bug):
```java
public void testPathWithAmpersand() throws Exception {
    FileEndpoint endpoint = context.getEndpoint(
        "file://target/data/Darjeeling & Jalpaiguri", FileEndpoint.class);
    // This works even on buggy version because there is no query string,
    // so & is never mis-parsed as a parameter separator.
    assertNotNull(endpoint);
}
```