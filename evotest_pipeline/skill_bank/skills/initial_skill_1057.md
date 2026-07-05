---
name: package-mapper-url-encoding-state-reuse
description: When building encoded URLs with query parameters, ensure internal mutable
  state used for URL construction is not shared across requests. Test that encoding
  multiple URLs correctly handles each set of parameters independently, returning
  non-null results.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# package-mapper-url-encoding-state-reuse

## Instructions

# PackageMapper URL Encoding State Reuse Bug

## Instructions

- WHEN the TG encounters a `PackageMapper` or similar URL mapper class that builds encoded URLs using an internal mutable state (e.g., a `StringBuilder` or reusable `Url` instance), and the encoding method accepts parameters (like page class name, page parameters, URL attributes) that are combined into a single URL string:
  - THEN the TG should write a parametric/state test that calls the encode method **at least twice sequentially** with **different query parameters** on the same mapper instance, and verify that the second result is non-null and correctly contains its own parameters.
  - The bug: If the mapper reuses an internal mutable `Url` object (or similar state) across invocations without properly resetting it between calls, the second call may return `null` or incorrect results because the internal state is corrupted by the first call.
  - The test should specifically check that a URL **with query parameters** (e.g., `?a=b&c=d`) followed by another URL **with different query parameters** (e.g., `?e=f&g=h`) both produce non-null, valid results, **not** just that the first call works.
  - Common pitfall: Testing only a single URL encoding call per mapper instance, which would miss state corruption bugs that only manifest on the second or subsequent call.
  - Correct example: create one `PackageMapper`, call `encode(...)` with pageClass and parameters1, assert non-null and correct; then call `encode(...)` again with the same pageClass but different parameters2, assert non-null and correct — the second call should NOT return null.
  - Incorrect example: creating a fresh mapper for each test case, or only verifying the first encode call.

### Concrete Values/Examples

- Triggering test method: `encode5` in `PackageMapperTest` which calls `mapper.encode(mapper.mapTo(mockRequest, pageClass, params1))` and then `mapper.encode(mapper.mapTo(mockRequest, pageClass, params2))` and asserts both return non-null URLs with the correct parameters.
- The mapper class is `org.apache.wicket.core.request.mapper.PackageMapper`.
- The encode method returns a `CharSequence` (URL string). The bug causes the second call to return `null` when the internal `Url` object is reused without clearing.
- When testing, use the same mapper instance for multiple encode calls, varying only the page parameters (e.g., `PageParameters` with different key-value pairs).
- Verify the returned URL contains the expected query string for each set of parameters, not just that it's non-null.