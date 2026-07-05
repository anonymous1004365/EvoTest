---
name: encrypted-url-additional-query-parameters
description: When a CryptoMapper decrypts an encrypted URL, additional query parameters
  appended to the encrypted URL (beyond those in the encrypted payload) must be preserved
  and passed through. This skill teaches testing that decryption preserves both original
  encrypted parameters and extra non-encrypted URL query parameters.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
- PARAMETER_PASS_THROUGH
- DECRYPTION
test_pattern: STATE_TEST
---

# encrypted-url-additional-query-parameters

## Instructions

# Encrypted URL Additional Query Parameters Preservation

## Instructions

- WHEN the TG encounters a `CryptoMapper` (or similar encrypted URL mapper) that decrypts URLs by calling `decryptUrl(Request, Url)` and then reconstructing the `Url` object — specifically a class that parses a decrypted URL string back into a `Url` object and copies its `getQueryParameters()` to the resulting URL
- THEN the TG should test that **additional query parameters appended directly to the encrypted URL** are preserved in the decrypted result. Specifically:
  1. Create an encrypted URL using `mapper.mapHandler(...)` with a `RequestHandler` that has page parameters (e.g., `PageParameters` with `"key1=value1"`)
  2. Then construct a `Request` whose `Url` is based on that encrypted URL, but **add extra query parameters** to the `Url` that were NOT part of the original encrypted payload (e.g., `"extraKey=extraValue"`)
  3. Call `mapper.mapRequest(request)` to decrypt
  4. Verify that the resulting handler (unwrapped through `RequestSettingRequestHandler`) contains BOTH the original parameters (e.g., `"key1=value1"`) AND the extra parameters (e.g., `"extraKey=extraValue"`)
- WHEN testing this scenario, verify that the extra parameter value is NOT null — the bug occurred when decrypting returned `null` for the extra parameter value on the buggy version
- Include a test case where the encrypted URL has additional query parameters that were NOT part of the original encryption, simulating a request that arrives with extra tracking parameters or state appended to the encrypted URL
- Common pitfalls to avoid:
  - Testing only the decryption of the encrypted payload without considering extra parameters on the URL
  - Forgetting to unwrap `RequestSettingRequestHandler` to access the delegate handler's parameters
  - Testing only `PageParameters` equality without checking individual parameter values for null
  - Assuming that `url.getQueryParameters().addAll(originalUrl.getQueryParameters())` without also adding `encryptedUrl.getQueryParameters()` is sufficient — the fix adds a second `addAll` call to merge in the encrypted URL's own query parameters

### Correct Example
```java
@Test
public void additionalParameters()
{
    PageParameters expectedParameters = new PageParameters();
    expectedParameters.add("key1", "value1");
    RenderPageRequestHandler renderPageRequestHandler = new RenderPageRequestHandler(
        new PageProvider(DummyHomePage.class, expectedParameters));
    Url encrypted = mapper.mapHandler(renderPageRequestHandler);
    
    // Add extra query parameter to the encrypted URL (simulating an appended tracking parameter)
    encrypted.setQueryParameter("trackingKey", "trackingValue");
    
    Request request = getRequest(encrypted);
    IRequestHandler requestHandler = mapper.mapRequest(request);
    assertTrue(requestHandler instanceof RequestSettingRequestHandler);
    requestHandler = ((RequestSettingRequestHandler)requestHandler).getDelegateHandler();
    assertTrue(requestHandler instanceof RenderPageRequestHandler);
    
    RenderPageRequestHandler handler = (RenderPageRequestHandler)requestHandler;
    PageParameters actualParameters = handler.getPageParameters();
    
    // Original encrypted parameter must be present
    assertEquals("value1", actualParameters.get("key1").toOptionalString());
    // Additional parameter from the URL must also be present (not null!)
    assertEquals("trackingValue", actualParameters.get("trackingKey").toOptionalString());
}
```

### Incorrect Example (would miss the bug)
```java
@Test
public void additionalParameters()
{
    // Only tests encrypted parameters, no extra URL parameters
    PageParameters expectedParameters = new PageParameters();
    expectedParameters.add("key1", "value1");
    RenderPageRequestHandler renderPageRequestHandler = new RenderPageRequestHandler(
        new PageProvider(DummyHomePage.class, expectedParameters));
    Url encrypted = mapper.mapHandler(renderPageRequestHandler);
    
    Request request = getRequest(encrypted);  // Missing: adding extra query params
    IRequestHandler requestHandler = mapper.mapRequest(request);
    // ... would pass on both buggy and fixed, not catching the regression
}
```