---
name: http-options-method-handling
description: When a servlet filter handles HTTP OPTIONS requests, the TG should verify
  that the filter intercepts OPTIONS requests early and returns a proper response
  (200 status with Allow header) without proceeding to normal request processing (resource
  resolution, request cycle execution). This bug occurred because an OPTIONS request
  was processed through the normal wicket request cycle instead of being handled early.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# http-options-method-handling

## Instructions

# HTTP OPTIONS Method Handling in Servlet Filters

## Instructions

- WHEN the TG encounters servlet filter code that checks for HTTP method (e.g., `"OPTIONS".equalsIgnoreCase(httpServletRequest.getMethod())`) and returns early
- THEN the TG should verify that OPTIONS requests are intercepted by:
  1. Setting `httpServletRequest.setMethod("OPtioNS")` — use mixed-case to test that the comparison is case-insensitive via `equalsIgnoreCase()`
  2. NOT proceeding to resource resolution / request cycle execution — the test should verify that the filter returns a 200 (SC_OK) status code with an "Allow" header containing method names (e.g., "GET,POST,OPTIONS,PUT,HEAD,PATCH,DELETE,TRACE") and "Content-Length" set to "0"
  3. The test must not invoke any resource that would be resolved during normal processing — e.g., do not register a mock resource that triggers `fail("should never get here")` and then verify it wasn't called; instead verify the response status and headers directly

- Common pitfalls to avoid:
  - **Testing with only uppercase "OPTIONS"**: The method comparison uses `equalsIgnoreCase()`, so the test MUST use mixed case (e.g., "OPtioNS" or "options") to verify case-insensitivity works correctly
  - **Falling through to normal request processing**: Verify that the filter does NOT reach any code path that resolves resources or calls `application.createRequestCycle(...)` — this is the essence of the bug
  - **Using only mock/verify patterns**: Instead of verifying that a resource's `newResourceResponse()` was never called (which would require a mock), test the actual HTTP response (status code, headers) that the filter returns for an OPTIONS request

### Correct approach

```java
@Test
public void options() throws Exception
{
    MockHttpServletRequest request = new MockHttpServletRequest(application, null, null);
    request.setURL(request.getContextPath() + request.getServletPath() +
        "/wicket/resource/" + Application.class.getName() + "/foo.txt");
    request.setMethod("OPtioNS");  // use mixed case to test equalsIgnoreCase
    MockHttpServletResponse response = new MockHttpServletResponse(request);
    filter.doFilter(request, response, chain);
    assertEquals(HttpServletResponse.SC_OK, response.getStatus());
    assertNotNull(response.getHeader("Allow"));
    assertNotNull(response.getHeader("Content-Length"));
}
```

### Incorrect approach

```java
@Test
public void options_WRONG() throws Exception
{
    MockHttpServletRequest request = new MockHttpServletRequest(application, null, null);
    request.setURL(...);
    request.setMethod("OPTIONS");  // BUG: only tests uppercase, not case-insensitivity
    MockHttpServletResponse response = new MockHttpServletResponse(request);
    filter.doFilter(request, response, chain);
    // BUG: doesn't verify that resource resolution was skipped
    // BUG: doesn't check response status/headers
}
```