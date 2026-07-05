---
name: web-page-renderer-test-setup
description: When testing a WebPageRenderer that delegates to overridable hook methods
  (shouldRedirectToTargetUrl, shouldRenderPageAndWriteResponse, shouldPreserveClientUrl),
  tests must set up a custom subclass that controls these hooks to exercise specific
  render paths.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ARRAY_ITERATION
test_pattern: STATE_TEST
---

# web-page-renderer-test-setup

## Instructions

# WebPageRenderer Hook Method Testing

## Instructions

- WHEN the TG encounters a `WebPageRenderer` or `PageRenderer` subclass that delegates to hook methods like `shouldRedirectToTargetUrl(RequestCycle, Url)`, `shouldRenderPageAndWriteResponse(RequestCycle, Url)`, or `shouldPreserveClientUrl(RequestCycle)` — all of which return `boolean`
- THEN the TG should create a concrete test subclass (e.g., `TestPageRenderer`) that extends `WebPageRenderer` and overrides these hook methods to return controlled values, rather than mocking the entire renderer
- The test should verify the correct render path is taken based on the returned boolean values (e.g., when `shouldRenderPageAndWriteResponse` returns `false` for a redirect scenario, the renderer should not attempt to write the response; when `shouldPreserveClientUrl` returns `true`, the renderer should preserve the client URL)
- Include tests where the method is called with `null` `RequestCycle` to verify the method handles a null argument gracefully (e.g., `shouldRedirectToTargetUrl(null, Url.parse("test"))`)
- Common pitfalls:
  - Mocking `WebPageRenderer` instead of using a real subclass — mocking makes it impossible to test the actual delegation logic
  - Not testing the `null` `RequestCycle` case — the buggy version may have failed when called with `null` due to missing null checks before dereferencing request cycle state
  - Only testing one boolean combination (e.g., all `false`) without also testing the opposite combination (e.g., `true` for some hooks) to ensure both branches are exercised

### Correct example
```java
// Test subclass controlling hooks
class TestPageRenderer extends WebPageRenderer {
    boolean shouldRedirectResult;
    
    @Override
    protected boolean shouldRedirectToTargetUrl(RequestCycle rc, Url u) {
        return shouldRedirectResult;
    }
    
    @Override
    protected boolean shouldRenderPageAndWriteResponse(RequestCycle rc, Url u) {
        return false;
    }
}

// Test usage
TestPageRenderer renderer = new TestPageRenderer();
renderer.shouldRedirectResult = true;
assertTrue(renderer.shouldRedirectToTargetUrl(requestCycle, Url.parse("test")));
```

### Incorrect example
```java
// Mocking — loses the actual delegation behavior
WebPageRenderer renderer = mock(WebPageRenderer.class);
// Cannot verify the real shouldRenderPage... logic
```