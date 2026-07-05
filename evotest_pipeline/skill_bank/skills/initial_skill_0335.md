---
name: encrypted-url-decoding-with-empty-query-string
description: ''
code_tags:
- ARRAY_LIST_INDEX_OUT_OF_BOUNDS
- STRING_MANIPULATION
- REQUEST_PROCESSING_DECODING
test_pattern: EXCEPTION_TEST
---

# encrypted-url-decoding-with-empty-query-string

## Instructions

# Encrypted URL Decoding With Empty Query String

## Instructions

- WHEN the TG encounters a class that implements `decode(Request)` and calls `decodeURL(url)` on the full URL (which may contain path and optional query string), THEN it should test with:
  - A URL containing **no `?` character at all** (e.g., `"/mypage"`)
  - A URL containing a `?` character with **nothing after it** (e.g., `"/mypage?"`)
- WHEN the URL has no query string, the `decodedQueryParams` return value from `decodeURL(url)` will be `null`, and the code must gracefully fall through to calling `defaultStrategy.decode(request)` without attempting to create a `DecodedUrlRequest`.
- WHEN `decodeURL(url)` throws a `StringIndexOutOfBoundsException` (e.g., when calling `url.substring(...)` on a URL with no `?` or with `?` at the end), THEN the test must verify that a `WicketRuntimeException` is thrown by `decode(Request)` (since the catch block wraps it).
- Common pitfalls:
  - Testing only with valid query strings (e.g., `"/mypage?param=value"`)
  - Not testing boundary cases where the URL has no `?` or `?` at the very end with no characters after it
  - Assuming `decodeURL()` always returns a non-null value for any URL containing `?`
  - Not verifying that the exception type is `WicketRuntimeException` (not just any exception)

### Correct test example

```java
public void testDecodeUrlWithNoQueryString()
{
    // Create a mock Request that returns a URL without '?'
    Request request = new Request() {
        @Override
        public String getURL() {
            return "/some/path/no/querystring";
        }
        @Override
        public String decodeURL(String url) {
            return url;
        }
    };
    CryptedUrlWebRequestCodingStrategy strategy = new CryptedUrlWebRequestCodingStrategy(mockStrategy);
    // Should not throw any exception
    RequestParameters params = strategy.decode(request);
    assertNotNull(params);
}

public void testDecodeUrlWithEmptyQueryString()
{
    // Create a mock Request that returns a URL with '?' but nothing after
    Request request = new Request() {
        @Override
        public String getURL() {
            return "/some/path?";
        }
        @Override
        public String decodeURL(String url) {
            return url;
        }
    };
    CryptedUrlWebRequestCodingStrategy strategy = new CryptedUrlWebRequestCodingStrategy(mockStrategy);
    // Should not throw any exception
    RequestParameters params = strategy.decode(request);
    assertNotNull(params);
}
```

### Common mistake (test that would miss the bug)

```java
// Only tests valid query strings — misses the empty/no-query-string cases
public void testDecodeUrlWithValidQueryString()
{
    Request request = new Request() {
        @Override
        public String getURL() {
            return "/page?x=encryptedValue";
        }
        @Override
        public String decodeURL(String url) {
            return url;
        }
    };
    CryptedUrlWebRequestCodingStrategy strategy = new CryptedUrlWebRequestCodingStrategy(mockStrategy);
    RequestParameters params = strategy.decode(request);
    // This test passes even when the bug exists — insufficient coverage
}
```