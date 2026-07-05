---
name: redirect-url-encoding-validation
description: WHEN testing sendRedirect methods that involve two-step URL encoding
  (encodeRedirectURL then sendRedirect), THEN write tests that verify the final URL
  passed to the servlet's sendRedirect matches the original URL, not the encoded one.
  This skill applies when URL redirection logic potentially double-encodes or incorrectly
  transforms the URL.
code_tags:
- URL_HANDLING
test_pattern: INTERACTION_TEST
---

# redirect-url-encoding-validation

## Instructions

# Redirect URL Encoding Validation

## Instructions

WHEN the TG encounters a `sendRedirect(String url)` method that:
1. First calls `httpServletResponse.encodeRedirectURL(url)` to encode the URL, AND
2. Then passes the **encoded** result to `httpServletResponse.sendRedirect(encodedUrl)`,

THEN the TG should write a test that:
- Uses Mockito mocks (or similar) for the underlying `HttpServletResponse`
- Mocks `encodeRedirectURL(...)` to return a **different** string than the input (e.g., return `"someOtherUrl"` regardless of input, or a clearly distinguishable encoded form)
- Passes the original URL to the method under test
- Verifies that `httpServletResponse.sendRedirect(...)` is called with the **original, unencoded URL** — NOT the return value of `encodeRedirectURL`
- If the buggy code passes the encoded URL to `sendRedirect()` instead of the original URL, the test should fail on the buggy version

The TG should **avoid** these common mistakes:
- ❌ Mocking `encodeRedirectURL` to return the same string as its input (this masks the bug)
- ❌ Only verifying that `sendRedirect` was called without checking what argument was passed
- ❌ Using `anyString()` matcher for the `sendRedirect` argument verification

### Correct Example (Bug-Detecting Test)

```java
@Test
public void sendRedirect()
{
    // mock the underlying HttpServletResponse
    String url = "relative/path?param=value";
    
    // Make encodeRedirectURL return a DIFFERENT string to catch the bug
    when(httpServletResponse.encodeRedirectURL(anyString())).thenReturn("encodedUrl");
    
    // Execute
    response.sendRedirect(url);
    
    // Verify: sendRedirect should be called with the ORIGINAL url, not the encoded one
    verify(httpServletResponse).sendRedirect(url);
    // The buggy version would pass "encodedUrl" to sendRedirect instead
}
```

### Incorrect Example (Masks the Bug)

```java
@Test
public void sendRedirect()
{
    String url = "relative/path?param=value";
    
    // BUG: encodeRedirectURL returns the same string, so the bug is invisible
    when(httpServletResponse.encodeRedirectURL(anyString())).thenAnswer(
        invocation -> invocation.getArgument(0));
    
    response.sendRedirect(url);
    
    // This would pass on both buggy and fixed versions
    verify(httpServletResponse).sendRedirect(url);
}
```

### Pitfalls

- **Masking the bug**: If `encodeRedirectURL` returns the same value as its input, the test won't distinguish between buggy and fixed code. Always make the mock return a **visibly different** value.
- **Verifying with anyString()**: Using `verify(httpServletResponse).sendRedirect(anyString())` will pass regardless of what argument is passed — this defeats the purpose of testing which URL is sent.
- **Testing only the encodeRedirectURL call**: The bug is not about whether `encodeRedirectURL` is called — it's about whether the **return value of `encodeRedirectURL`** is used in place of the original URL when calling `sendRedirect`. Make sure to verify the argument to `sendRedirect`, not just that `encodeRedirectURL` was called.