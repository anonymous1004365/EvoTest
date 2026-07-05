---
name: cookie-preservation-across-redirect
description: When testing cookie handling across request handler redirects, verify
  that cookies set before a NonResettingRestartException are not lost by the BufferedWebResponse.writeTo()
  operation. The cookie collection should maintain order-preserving semantics during
  metadata transfer.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# cookie-preservation-across-redirect

## Instructions

# Cookie Preservation Across Redirect Handlers

## Instructions

- WHEN the TG encounters code that creates a `BufferedWebResponse`, sets cookies on it, and then has its metadata transferred to another response (e.g., via `writeMetaData()`), AND the transfer is triggered by a `NonResettingRestartException` (which is a `ReplaceHandlerException`):
  - THEN the TG should write a test that:
    1. Creates a `BufferedWebResponse` wrapping an `HttpServletResponse`
    2. Adds at least one `Cookie` to the `BufferedWebResponse` (e.g., via `response.addCookie(myCookie)`)
    3. Creates a second `BufferedWebResponse` that receives the metadata via `writeMetaData(originalResponse)`
    4. Verifies that after the transfer, the second response contains the same cookies (same count, same name/value/domain/path properties)
    5. Specifically tests that the operation does NOT clear/reset cookies during the transfer — the failure manifests as `expected:<1> but was:<0>` when checking cookie count after transfer
  - Use concrete types: `BufferedWebResponse`, `javax.servlet.http.Cookie`, `org.apache.wicket.protocol.http.IMetaDataBufferingWebResponse`
  - The test should expect `1` cookie to be present after `writeMetaData()` — on the buggy version the count will be `0`

- Common pitfalls to avoid:
  - Testing cookies by serializing the response and checking the header string rather than inspecting the `BufferedWebResponse`'s internal cookie collection directly
  - Testing only `ServletWebResponse` behavior without involving `BufferedWebResponse` as the wrapper
  - Forgetting that `writeMetaData` accepts a `WebResponse` parameter, and the bug occurs specifically when that source response is a `BufferedWebResponse` containing cookies
  - Testing only cookie addition/removal but not testing the transfer of cookies between buffered responses via `writeMetaData()`
  - Assuming the internal cookie list uses a `Set` when it actually uses a `List` — order-dependent semantics matter

- **Correct example** (verifies cookie survived transfer):
```java
BufferedWebResponse originalResponse = new BufferedWebResponse(servletResponse);
Cookie testCookie = new Cookie("testName", "testValue");
originalResponse.addCookie(testCookie);

BufferedWebResponse targetResponse = new BufferedWebResponse(servletResponse);
targetResponse.writeMetaData(originalResponse);

// Verify cookie was preserved
assertEquals(1, targetResponse.getCookies().size());
assertEquals("testName", targetResponse.getCookies().get(0).getName());
```

- **Incorrect example** (only tests cookie on the original response, missing the transfer bug):
```java
BufferedWebResponse originalResponse = new BufferedWebResponse(servletResponse);
Cookie testCookie = new Cookie("testName", "testValue");
originalResponse.addCookie(testCookie);

// WRONG: Only checks cookies on the original response, not after transfer
assertEquals(1, originalResponse.getCookies().size());
// Missing: targetResponse.writeMetaData(originalResponse) and checking targetResponse
```