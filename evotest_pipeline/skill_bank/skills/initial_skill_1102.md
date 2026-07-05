---
name: render-strategy-state-mutation
description: ''
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# render-strategy-state-mutation

## Instructions

# Render Strategy State Mutation Handling

## Instructions

- WHEN the TG encounters a `WebPageRenderer` (or similar renderer) that has a fallback action / strategy field (e.g., `private Action fallbackAction`) that is mutated during the `respond()` method, and where URL rendering decisions depend on this field's value,
  - THEN the TG should write a test that:
    1. Creates a **mock/stub request cycle** and page instance, where the first render attempt is configured to produce a specific URL (e.g., a redirect URL or a "one-pass" render URL).
    2. **Sets the renderer's state to a conflicting mode** (e.g., calling a method like `setAlwaysRedirect(true)` *after* the initial `respond()` call but before a second `respond()` call), simulating a scenario where the renderer decision changes mid-lifecycle.
    3. Calls `respond()` a **second time** and verifies that the **second response** correctly uses the new strategy (e.g., a redirect) rather than reusing the cached/stale decision from the first call.
    4. Asserts that the `targetUrl` (or equivalent response target) is not overwritten by a null/empty fallback that was left stale from the first pass.
  - Include concrete values: for Wicket tests, simulate a `PageRenderer` initialized via `new WebPageRenderer(page)` with a mock `RequestCycle` that returns `RedirectResponse` vs `StringResponse`.
  - Expected behavior on buggy version: the second `respond()` call produces an incorrect response (e.g., a rendered page instead of a redirect, or vice versa). The test should assert against the final response type, not intermediate state.
  - Common pitfalls:
    - Testing only a single `respond()` call — the bug manifests only on the **second** call after state mutation.
    - Not resetting/verifying the response object between calls — the TG may check the wrong response instance.
    - Assuming `redirectToTargetUrl` vs `shouldRenderPageAndWriteResponse` is always consistent — they can diverge when fallback state is stale.
  - Correct example (pseudocode):
    ```java
    // Arrange
    RequestCycle cycle = mock(RequestCycle.class);
    IRequestHandler target = mock(IRequestHandler.class);
    when(cycle.getUrlRenderer()).thenReturn(new UrlRenderer(cycle));
    when(cycle.replaceResponse(any())).thenAnswer(invocation -> {
        ((Response) invocation.getArgument(0)).close();
        return null;
    });

    WebPageRenderer renderer = new WebPageRenderer(page);
    renderer.respond(cycle);  // first call — produces one response
    
    // Act: mutate state mid-lifecycle
    renderer.setAlwaysRedirect(true);
    // Now the second call should use the new strategy
    renderer.respond(cycle);

    // Assert: verify the final response is a redirect
    // (on buggy version, final response is still the stale one-pass render)
    ```
  - Incorrect example (pitfall):
    ```java
    // BAD: only tests first respond call
    WebPageRenderer renderer = new WebPageRenderer(page);
    renderer.respond(cycle);
    // never changes state between calls – misses the bug entirely
    ```