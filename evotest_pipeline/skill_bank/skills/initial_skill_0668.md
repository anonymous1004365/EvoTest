---
name: redirect-to-buffer-for-nonversioned-page
description: When a RestartResponseAtInterceptPageException is thrown in an authorization
  check and the page is non-versioned (e.g., not implementing PageSettings#getVersionedPages()),
  the redirect buffer may be null. This skill teaches the TG to test that the redirectToBuffer
  method handles null buffers gracefully without a NullPointerException.
code_tags:
- AUTHORIZATION_EXCEPTION_PROPAGATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# redirect-to-buffer-for-nonversioned-page

## Instructions

# Redirect to Buffer for Non-Versioned Pages

## Instructions

- WHEN the TG encounters `RestartResponseAtInterceptPageException` being thrown in an authorization context (e.g., authentication interceptor) and the code calls `redirectToBuffer()` or `getRedirectToBuffer()` to store the original URL for later restoration
- THEN the TG should write a test that:
  1. Creates an instance of a `NonVersionedPage` — a page whose class name returns `false` from `PageSettings#isVersioned()` or that does not have `IPageSettings` returning it as versioned
  2. Throws `RestartResponseAtInterceptPageException` targeting that non-versioned page
  3. Verifies that the exception does NOT throw a `NullPointerException` when `redirectToBuffer()` is called on a `Response` whose buffer is `null` (i.e., `getStringRepresentation()` returns `null`)
  4. Asserts that the original URL is properly stored and can be retrieved via `getOriginalUrl()` on the redirect buffer
- Common pitfalls:
  - Testing only with versioned pages (which have a non-null buffer), leaving the non-versioned path untested
  - Assuming `getStringRepresentation()` always returns non-null — wrap with a null check before calling methods on it
  - Forgetting to test that the exception propagates correctly (i.e., it IS thrown and caught, not swallowed)
  - Not using `assertNotNull` on the redirect buffer's stored URL before asserting its value

### Correct Example (what the test should do)

```java
@Test
public void redirectToBufferForNonVersionedPage()
{
    try
    {
        // Simulate that there is a buffered response that stores the original URL
        // and that getStringRepresentation() returns null (non-versioned page case)
        Page page = new NonVersionedPage();
        throw new RestartResponseAtInterceptPageException(page);
    }
    catch (RestartResponseAtInterceptPageException e)
    {
        // The fix: redirectToBuffer should handle null getStringRepresentation()
        // Without the fix, this would throw NullPointerException
        String originalUrl = e.getRedirectToBuffer().getOriginalUrl();
        assertNotNull("Original URL should be preserved", originalUrl);
    }
}
```

### Incorrect Example (what to avoid)

```java
@Test
public void redirectToBufferForVersionedPageOnly()
{
    // BUG: Only tests with versioned pages that have non-null buffer
    // This passes on the buggy code and never catches the NPE
    Page page = new VersionedPage();
    RestartResponseAtInterceptPageException ex = 
        new RestartResponseAtInterceptPageException(page);
    // Assuming getStringRepresentation() is always non-null
    assertNotNull(ex.getRedirectToBuffer().getOriginalUrl());
}
```