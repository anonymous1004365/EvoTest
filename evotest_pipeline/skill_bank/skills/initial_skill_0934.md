---
name: homepage-url-encryption-roundtrip
description: WHEN testing URL encryption/decryption with CryptoMapper, THEN the TG
  should verify that encrypting and then decrypting a URL produces exactly the original
  URL — including for custom home page URLs that have no mount path but have query
  parameters (page parameters).
code_tags:
- ENCRYPTED_URL_ROUNDTRIP
- HOMEPAGE_ENCRYPTION_BEHAVIOR
test_pattern: PARAMETRIC_TEST
---

# homepage-url-encryption-roundtrip

## Instructions

# Homepage URL Encryption Roundtrip

## Instructions

WHEN the TG encounters code that encrypts and decrypts URLs using `CryptoMapper`, where a URL might represent a home page request (no path segments beyond the root) but carry query parameters (page parameters):

- THEN the TG should write a **roundtrip test** that:
  1. Creates a `Url` object representing the home page URL with parameters (e.g., `Url.parse("?param1=value1&param2=value2")`)
  2. Encrypts it using `CryptoMapper.encryptUrl()` — note: in the source, the encryption is done implicitly by calling `mapRequest()` on a `Request` object whose URL is set to this home page URL
  3. Decrypts the encrypted URL back using `CryptoMapper.decryptUrl()`
  4. **Asserts** that the decrypted URL equals the original home page URL exactly (same path segments, same query parameters)

- **Concrete example from this bug:** The buggy `CryptoMapper` implementation produced an extra path segment `/0lh9b` appended to the home page URL after roundtrip encryption/decryption. The fixed version preserves the original URL correctly.

- **Common pitfalls:**
  - Testing only with named mounted pages (e.g., `/myPage?param=value`) and **not** testing with the bare home page URL that has only query parameters and no path segments.
  - Assuming that `encryptUrl` and `decryptUrl` are the methods to test — the bug manifests when the mapper processes a `Request` with a home page URL, so the test should simulate a full request cycle: create a `Request` with the home page URL, call `mapRequest()`, and check the resulting URL after decryption.
  - Not including query parameters (page parameters) in the test — many encryption bugs only surface when URL parameters are present.

- **When writing the test:**
  ```java
  // CORRECT approach: test bare home page URL with query parameters roundtrip
  Url originalUrl = Url.parse("?param1=value1&param2=value2");
  Request request = new Request() {
      @Override
      public Url getUrl() { return originalUrl; }
      // ... implement other abstract methods minimally
  };
  IRequestHandler handler = cryptoMapper.mapRequest(request);
  Url decryptedUrl = cryptoMapper.decryptUrl(request, handler.getUrl());
  assertEquals(originalUrl, decryptedUrl);
  ```

- **Mistakes to avoid:**
  ```java
  // WRONG: Only testing with a mounted page that has path segments
  Url originalUrl = Url.parse("mountedPage?param=value"); // This won't catch the home page bug
  
  // WRONG: Not checking equality of the full URL (path segments + parameters)
  assertEquals(originalUrl.getPath(), decryptedUrl.getPath());
  // This misses differences in query parameters
  ```

- The **key insight**: a home page URL (empty path, only query string) must roundtrip through encryption/decryption without gaining spurious path segments or losing parameters. The bug manifest is that the decrypted URL has an extra segment `/0lh9b` appended, which is an internal encryption artifact leaking into the decrypted output.