---
name: crypto-mapper-url-resource-reference-testing
description: When testing CryptoMapper wrapping UrlResourceReference objects, test
  that resource references with fully-qualified URLs (e.g., "https://example.org/script.js")
  are correctly encrypted/decoded through the mapper cycle, and verify the round-trip
  produces the original URL even when the request has no host information.
code_tags:
- URL_CONSTRUCTION
- ENCRYPTION_DECORATION
- RESOURCE_REFERENCE_MAPPING
test_pattern: INTERACTION_TEST
---

# crypto-mapper-url-resource-reference-testing

## Instructions

# CryptoMapper UrlResourceReference Testing

## Instructions

- WHEN the TG encounters `CryptoMapper` wrapping any `IRequestMapper` (e.g., `UrlResourceReferenceMapper`) and the mapper is used to process `UrlResourceReference` instances that contain fully-qualified URLs (with scheme and host, like `"https://example.org/script.js"`)
- THEN the TG should write a test that:
  1. Creates a `UrlResourceReference` with a fully-qualified URL (e.g., `Url.parse("https://www.google.com/jsapi")`)
  2. Wraps the real `UrlResourceReferenceMapper` in a `CryptoMapper` (e.g., `new CryptoMapper(new UrlResourceReferenceMapper(), ...)`)
  3. Calls `mapper.mapRequest(RequestMapper.this)` on the request that corresponds to the encrypted URL
  4. Verifies that the mapped `Requestable` returned by `CryptoMapper` is a `UrlResourceReference` whose `getUrl()` returns the **original fully-qualified URL** (e.g., `"https://www.google.com/jsapi"`)
  5. Verifies the round-trip: `<mapper>.mapRequest(mapper.mapRequest(...))` yields the original requestable
- Common pitfalls to avoid:
  - Testing only with relative URLs or internal Wicket resource references (e.g., `ResourceReference("package", "style.css", ...)`) instead of `UrlResourceReference` with absolute URLs
  - Using mocked `IRequestMapper` instead of the real `UrlResourceReferenceMapper` — the bug is specific to how `UrlResourceReferenceMapper` handles `UrlResourceReference` objects, and mocking would miss the integration issue
  - Testing only the encryption direction (request → encrypted URL → decrypted request) without testing the full mapper cycle (`mapRequest` → `mapRequest`) — the bug manifests when the decrypted `UrlResourceReference` gets rendered to a URL by `CryptoMapper`
  - Assuming that any `ResourceReference` works the same as `UrlResourceReference` — the bug is specific to `UrlResourceReference` which carries its own pre-built URL

### Example: Correct Test (simplified)

```java
@Test
public void urlResourceReference() 
{
    Url url = Url.parse("https://www.google.com/jsapi");
    
    IRequestMapper mapper = new UrlResourceReferenceMapper();
    
    CryptoMapper cryptoMapper = new CryptoMapper(mapper, getWicketSession());
    
    UrlResourceReference ref = new UrlResourceReference(url);
    
    Request request = ... // create request for the resource reference
    Requestable requestable = mapper.mapRequest(request);
    
    Url encrypted = cryptoMapper.mapRequest(request);
    Request decryptedRequest = ... // create request from encrypted URL
    Requestable result = cryptoMapper.mapRequest(decryptedRequest);
    
    assertTrue(result instanceof UrlResourceReference);
    assertEquals(url, ((UrlResourceReference) result).getUrl());
}
```

### Example: Incorrect Test (simplified)

```java
// BAD: Uses relative resource reference instead of UrlResourceReference
@Test
public void urlResourceReference_BAD() 
{
    IRequestMapper mapper = new UrlResourceReferenceMapper();
    CryptoMapper cryptoMapper = new CryptoMapper(mapper, getWicketSession());
    
    // Wrong: Using internal ResourceReference, not UrlResourceReference
    ResourceReference ref = new ResourceReference("my.page", "style.css", ...);
    
    // This test would pass even on buggy code because the bug only manifests
    // with UrlResourceReference objects
    ...
}
```