---
name: render-strategy-redirect-policy-combinatorics
description: When testing methods that combine multiple boolean flags and enum policies
  to determine render-or-redirect decisions, test all meaningful combinations of inputs
  to ensure the logic matches expectations for every configuration. Use the VariationIterator-based
  parametric approach from the existing test suite.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- REDIRECT_POLICY_LOGIC
- CONDITIONAL_BRANCH
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# render-strategy-redirect-policy-combinatorics

## Instructions

# Render Strategy & Redirect Policy Combinatorial Testing

## Instructions

WHEN the TG encounters a method like `shouldRenderPageAndWriteResponse(RequestCycle, Url, Url)` or `shouldRedirectToTargetUrl(RequestCycle, Url, Url)` in `WebPageRenderer` or `PageRenderer` that combines multiple boolean flags (ajax, onePassRender, redirectToRender, shouldPreserveClientUrl, targetEqualsCurrentUrl, newPageInstance, pageStateless) with a `RedirectPolicy` enum (REDIRECT_ALWAYS, NEVER_REDIRECT, AUTO_REDIRECT)...

THEN the TG should:
1. Create a combinatorial variation test that iterates over ALL combinations of the boolean parameters (or at minimum every combination that can trigger the bug).
2. Use a dedicated variation class (similar to `ShouldRenderPageAndWriteResponseVariations`) that extends `AbstractVariations` and chains `VariationIterator` objects for each boolean parameter.
3. Use a `TestPageRenderer` subclass to stub out the behavior (ajax, onePassRender, redirectToRender, redirectPolicy, shouldPreserveClientUrl, newPageInstance, pageStateless) and call the method under test.
4. Verify the result of each combination against the expected value by comparing with the test's oracle — a separate test method (e.g., `shouldRenderPageAndWriteResponseVariation()`) that iterates the variation and asserts the outcome.
5. Check that for the failing combination: `ajax=true, onePassRender=false, redirectToRender=false, redirectPolicy=ALWAYS_REDIRECT, shouldPreserveClientUrl=true, targetEqualsCurrentUrl=false, newPageInstance=false, pageStateless=false` — when `shouldPreserveClientUrl` is `true` and the redirect policy is `ALWAYS_REDIRECT` with a non-AJAX-render strategy, the method should return `false` (should NOT render and write response directly, but instead redirect).

Common pitfalls:
- Testing only a handful of ad-hoc scenarios instead of systematically covering all boolean flag combinations using a variation iterator.
- Forgetting to set the `shouldPreserveClientUrl` flag which interacts with the redirect policy to force a redirect even when other conditions (like same URLs) might suggest a direct render.
- Not resetting all state variables (ajax, onePassRender, redirectToRender, etc.) for each combination iteration.
- Using mocks that are too rigid — the `TestPageRenderer` approach of overriding boolean-returning methods directly is cleaner and avoids complex mocking setup.

Example of correct approach (from the existing test):
```java
// In the variation test, iterate all combinations
VariationIterator<RedirectPolicy> redirectPolicy = VariationIterator.of(Variation.of(RedirectPolicy.class));
VariationIterator<Boolean> ajax = VariationIterator.of(redirectPolicy, Variation.ofBoolean());
VariationIterator<Boolean> onePassRender = VariationIterator.of(ajax, Variation.ofBoolean());
VariationIterator<Boolean> redirectToRender = VariationIterator.of(onePassRender, Variation.ofBoolean());
VariationIterator<Boolean> shouldPreserveClientUrl = VariationIterator.of(redirectToRender, Variation.ofBoolean());
VariationIterator<Boolean> targetEqualsCurrentUrl = VariationIterator.of(shouldPreserveClientUrl, Variation.ofBoolean());
VariationIterator<Boolean> newPageInstance = VariationIterator.of(targetEqualsCurrentUrl, Variation.ofBoolean());
VariationIterator<Boolean> pageStateless = VariationIterator.of(newPageInstance, Variation.ofBoolean());

// For each combination, set up TestPageRenderer and call the method
TestPageRenderer renderer = new TestPageRenderer(null);
renderer.ajax = ajax.current();
renderer.onePassRender = onePassRender.current();
renderer.redirectToRender = redirectToRender.current();
renderer.redirectPolicy = redirectPolicy.current();
renderer.shouldPreserveClientUrl = shouldPreserveClientUrl.current();
renderer.newPageInstance = newPageInstance.current();
renderer.pageStateless = pageStateless.current();

boolean result = renderer.shouldRenderPageAndWriteResponse(null, 
    Url.parse("test"), targetEqualsCurrentUrl.current() ? Url.parse("test") : Url.parse("test2"));

// Then assert expected value — the test method should have an oracle
// that checks each combination against the correct expected value
```

Example of incorrect approach (missing coverage):
```java
// BAD: Only tests a single scenario
TestPageRenderer renderer = new TestPageRenderer(handler);
renderer.onePassRender = true;
// Missing: shouldPreserveClientUrl, redirectPolicy interaction
// Missing: exhaustive combination testing
```