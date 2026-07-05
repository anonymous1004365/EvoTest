---
name: crypto-mapper-non-encrypted-query-parameters
description: When testing an encryption/decryption mapper like CryptoMapper, verify
  that requests with non-encrypted query parameters to the home page are correctly
  handled (not rejected) and that the URL for the home page with non-encrypted parameters
  is NOT encrypted to avoid unnecessary redirects. Apply when the mapper has an optimization
  path that may skip encryption for certain URL patterns.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: STATE_TEST
---

# crypto-mapper-non-encrypted-query-parameters

## Instructions

# Testing Non-Encrypted Query Parameters on CryptoMapper

## Instructions

- WHEN the TG encounters a `CryptoMapper` (or similar encryption/decryption mapper) that wraps another `IRequestMapper` and has a `decryptUrl(Request, Url)` method that processes incoming URLs
- THEN the TG should test that the mapper correctly handles requests to the home page URL (empty segments, e.g., `Url.parse("")`) that carry **non-encrypted query parameters** like `?namedKey1=namedValue1`. The test must:
  1. **Map the handler**: Create a `RenderPageRequestHandler` with the home page class and `PageParameters` containing named parameters (e.g., `expectedParameters.add("namedKey1", "namedValue1")`). Call `mapper.mapHandler(renderPageRequestHandler)` and verify the resulting `Url` is NOT encrypted — it should match the original plain-text query string (e.g., `"?namedKey1=namedValue1"`).
  2. **Map the request back**: Create a `Request` from that URL using `getRequest(url)`, call `mapper.mapRequest(request)`, unwrap `IRequestHandlerDelegate` wrappers, and assert that the handler is a `RenderPageRequestHandler` for the home page with the correct page parameters (e.g., `handler.getPageParameters().get("namedKey1")` should return `"namedValue1"`).
  3. **Expect the query parameter to survive decryption**: Verify the decrypted handler preserves all original query parameter values.

- Common pitfalls to avoid:
  - **Testing only with encrypted URLs**: Do not assume all URLs must go through encryption. The mapper may optimize by leaving non-encrypted home page URLs as-is to avoid unnecessary redirects.
  - **Not testing the round-trip**: Both `mapHandler` (URL creation) and `mapRequest` (URL parsing) directions must be tested to catch inconsistency.
  - **Forgetting to unwrap delegates**: The mapped request handler may be wrapped in an `IRequestHandlerDelegate`. Use a helper like `unwrapRequestHandlerDelegate(requestHandler)` before asserting the handler type.
  - **Using an empty PageParameters**: The bug is specifically about non-encrypted parameters being passed through. An empty `PageParameters` would not trigger the buggy path.

### Correct test example (Java/JUnit):

```java
@Test
public void homePageWithNonEncryptedQueryParameters()
{
    PageParameters expectedParameters = new PageParameters();
    expectedParameters.add("namedKey1", "namedValue1");

    RenderPageRequestHandler renderPageRequestHandler = new RenderPageRequestHandler(
        new PageProvider(tester.getApplication().getHomePage(), expectedParameters));

    Url url = mapper.mapHandler(renderPageRequestHandler);
    assertEquals("?namedKey1=namedValue1", url.toString());

    Request request = getRequest(url);
    IRequestHandler requestHandler = mapper.mapRequest(request);
    assertNotNull(requestHandler);

    requestHandler = unwrapRequestHandlerDelegate(requestHandler);
    assertThat(requestHandler, instanceOf(RenderPageRequestHandler.class));
    RenderPageRequestHandler handler = (RenderPageRequestHandler) requestHandler;
    assertEquals(tester.getApplication().getHomePage(), handler.getPageClass());
    StringValue queryParam = handler.getPageParameters().get("namedKey1");
    assertEquals("namedValue1", queryParam.toOptionalString());
}
```

### Incorrect test example:

```java
// BAD: Only tests encrypted URL case, misses the non-encrypted path
@Test
public void bookmarkablePageEncrypt() {
    // ... tests encrypted bookmarkable URL only, never tests
    // home page with plain query params
}
```

```java
// BAD: Tests mapping in one direction only (missing round-trip)
@Test
public void testMapHandlerOnly() {
    Url url = mapper.mapHandler(handler);
    assertEquals("?key=val", url.toString());
    // Never verifies that mapRequest can decode this URL back
}
```