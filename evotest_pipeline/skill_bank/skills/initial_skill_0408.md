---
name: wicket-cookie-transfer-on-next-request
description: When a test writes a cookie via the response and expects it to be available
  on the next request (via getRequest().getCookies()), the TG should verify the cookie
  transfer logic. This skill is particularly relevant for BaseWicketTester / WicketTester
  cookie handling between requests.
code_tags:
- CACHING_AND_CONVERTER_REGISTRY
- NULL_CHECK
- ARGUMENT_VALIDATION
- COLLECTION_ITERATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# wicket-cookie-transfer-on-next-request

## Instructions

# Wicket Cookie Transfer on Next Request

## Instructions

WHEN the TG encounters code that adds cookies to a `MockHttpServletResponse` (e.g., via `response.addCookie(c)`) and expects those cookies to be available via `request.getCookies()` on the **next** simulated request, THEN the TG should write a test that:

1. Adds a cookie to the response during the first request processing.
2. Optionally call a method that triggers the cookie transfer (if such a method exists, e.g., `processCookies(...)` or `setLastRequest(...)`).
3. Makes a **second request** (not just reading `getRequest().getCookies()` on the same request).
4. Verifies that the cookie set in the first response is present in `getRequest().getCookies()` for the second request.

For example, a bug may occur where:
- The code iterates over the response cookies and transfers them to the request, but fails if the `CookieCollection` or `Cookies` wrapper's iterator does not return all elements correctly.
- The cookie transfer happens only on certain code paths (e.g., only when `processCookies(...)` is called) and is missing on other paths.

The test should make assertions like:
```java
// first request sets a cookie
tester.getRequest().addCookie(new Cookie("testCookie", "value"));
// process the request (e.g., tester.startPage(...))
// on the second request, the cookie should be available
tester.getRequest().addCookie(new Cookie("anotherCookie", "otherValue"));
// ...
// verify cookies from the first response are on the second request's cookies
Cookie[] cookies = tester.getRequest().getCookies();
assertNotNull("Cookies should not be null", cookies);
// assert that expected cookies exist
```

**Common pitfalls to avoid:**
- ❌ Testing that a cookie added to the request is available on the *same* request — this tests reading, not transfer.
- ❌ Only checking `getResponse().getCookies()` without checking the next request's `getCookies()`.
- ❌ Assuming the cookie transfer happens automatically without calling any intermediate method (e.g., `processCookies(...)`).
- ❌ Using a cookie with an expired max-age (0 or negative) which may be filtered out during transfer.
- ❌ Adding the cookie to the request directly rather than through the response and then relying on transfer logic.

**Correct example:**
```java
// Add cookie to response (e.g., via a page component setting a cookie)
// then make a second request
tester.startPage(MyPage.class);
// internally MyPage adds a cookie to the response
Cookie[] cookiesBefore = tester.getRequest().getCookies();
// ... make a new request (tester.startPage again)
// now verify the cookie was transferred to the new request
Cookie[] cookiesAfter = tester.getRequest().getCookies();
boolean found = false;
for (Cookie c : cookiesAfter) {
    if ("myCookieName".equals(c.getName())) {
        found = true;
        break;
    }
}
assertTrue("Cookie should have been transferred to the next request", found);
```

**Incorrect example:**
```java
// Only checking direct response cookies, not next request
tester.getRequest().addCookie(new Cookie("test", "val"));
Cookie[] cookies = tester.getRequest().getCookies();
assertTrue(cookies.length > 0); // This just verifies you can add/get on the same request, not transfer
```