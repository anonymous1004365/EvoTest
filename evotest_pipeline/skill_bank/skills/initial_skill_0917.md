---
name: renderer-redirect-decision-with-different-protocols
description: When testing renderers that make redirect/response decisions based on
  request and target URLs, test with URLs having different protocols (http vs https)
  to catch bugs in protocol-sensitivity logic. This skill helps detect missing protocol
  comparisons in conditional logic.
code_tags:
- NULL_CHECK
- VALIDATION
- ARRAY_INDEX_ACCESS
test_pattern: PARAMETRIC_TEST
---

# renderer-redirect-decision-with-different-protocols

## Instructions

# Renderer Redirect Decision with Different Protocols

## Instructions

**WHEN** the TG encounters a renderer class (like `WebPageRenderer` or `PageRenderer`) that has methods like `shouldRedirectToTargetUrl()` or `shouldRenderPageAndWriteResponse()` which compare request URLs with target URLs to make rendering decisions:

**THEN** the TG should:
1. Create tests that pass URLs with **different protocol schemes** (e.g., `http://example.com/page` vs `https://example.com/page`) to the request URL and target URL parameters
2. Verify that the method correctly handles cases where the request uses one protocol and the target URL uses a different protocol
3. Test all combinations: `http→http`, `http→https`, `https→http`, `https→https`
4. Verify against the expected boolean result — specifically check that the method does **not** incorrectly return `true` when it should return `false` due to protocol mismatch

**Common pitfalls to avoid:**
- Testing only with URLs that share the same protocol scheme (e.g., both `http://`)
- Assuming that only the path/query components matter for redirect/response decisions
- Not testing with `Url.parse("...")` to create URL objects — some implementations compare URL components which may include protocol/scheme
- Forgetting that `null` request cycles or `null` target URLs are boundary cases that should also be tested

**Example of what to avoid (too narrow):**
```java
// BAD: Only tests with same protocol
renderer.shouldRedirectToTargetUrl(requestCycle, Url.parse("http://example.com/page1"), Url.parse("http://example.com/page2"));
```

**Example of what to test:**
```java
// GOOD: Tests with different protocols
renderer.shouldRedirectToTargetUrl(requestCycle, Url.parse("http://example.com"), Url.parse("https://example.com"));
renderer.shouldRedirectToTargetUrl(requestCycle, Url.parse("https://example.com"), Url.parse("http://example.com"));
```

**Concrete implementation guidance:**
- Use `Url.parse(stringUrl)` to construct URL objects
- The `shouldRedirectToTargetUrl(requestCycle, targetUrl, currentUrl)` method from `WebPageRenderer` is the key method to test
- The bug is triggered when `shouldRedirectToTargetUrl` returns `true` (indicating a redirect should happen) but the protocol mismatch means a redirect to a different protocol can cause issues — the test should verify the correct boolean decision
- If the method under test returns `true` for same-protocol URLs and `false` for different-protocol URLs (or vice versa), verify this contract explicitly