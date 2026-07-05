---
name: ajax-base-url-validation
description: When a method parses a request header or parameter to construct a URL
  and then returns it as the response, the test should validate both the happy path
  (header present) and edge cases (header missing, parameter missing). This skill
  teaches how to write tests that catch bugs where a missing required header silently
  produces incorrect output instead of falling back to a sensible default or throwing
  an appropriate error.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# ajax-base-url-validation

## Instructions

# Ajax Base URL Validation

## Instructions

**WHEN** the TG encounters a method that reads a request header or parameter to construct a URL/path (e.g. `getClientUrl()` reading `"BaseUrl"` header or `"wicket-ajax-baseurl"` parameter):

- **THEN** the TG should write a test that:
  1. Mocks a ServletWebRequest where the header and parameter are both absent
  2. Calls the URL-getting method (e.g. `getClientUrl()`)
  3. Verifies the returned Url is NOT null
  4. Verifies the returned Url has an empty path (or the expected fallback behavior), NOT an arbitrary or incorrect path

- **Common pitfall #1**: Testing only the case where the header IS present. Without testing the missing-header case, a bug where the method mistakenly tries to parse a null/empty header value will go undetected.

- **Common pitfall #2**: Assuming that if no header is present, the method will throw an exception. Some implementations silently return a Url constructed from an empty/null string, which may produce incorrect results.

- **Common pitfall #3**: Forgetting to mock the `HttpServletRequest` to have no header returned (using `Mockito.when(request.getHeader("BaseUrl")).thenReturn(null)` or returning null by default).

### Example (Correct)

```java
@Test
public void getClientUrlAjaxWithoutBaseUrl()
{
    HttpServletRequest httpRequest = Mockito.mock(HttpServletRequest.class);
    when(httpRequest.getHeader("BaseUrl")).thenReturn(null);
    when(httpRequest.getParameter("wicket-ajax-baseurl")).thenReturn(null);
    when(httpRequest.getRequestURI()).thenReturn("/some/path");
    when(httpRequest.getQueryString()).thenReturn(null);

    ServletWebRequest request = new ServletWebRequest(httpRequest, "");
    Url url = request.getClientUrl();

    assertNotNull("Client URL must not be null", url);
    assertTrue("Client URL should have empty path when no base URL", url.getPath().isEmpty());
}
```

### Example (Incorrect)

```java
// BAD: Only tests happy path, does not test missing header case
@Test
public void getClientUrlAjaxWithBaseUrl()
{
    HttpServletRequest httpRequest = Mockito.mock(HttpServletRequest.class);
    when(httpRequest.getHeader("BaseUrl")).thenReturn("http://example.com/myapp/");
    // ... rest of test only validates the happy path
    
    // This test would PASS even if the method crashes on null header
}
```