---
name: redirect-policy-never-enforcement
description: When a class has a redirect policy that should prevent redirects (NEVER_REDIRECT),
  test that the policy is properly enforced even for AJAX requests with new stateless
  pages. The TG should verify the policy takes precedence over other conditions that
  would normally trigger a redirect.
code_tags:
- state_mutation
- validation
- null_check
- REDIRECT_POLICY_ENFORCEMENT
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: STATE_TEST
---

# redirect-policy-never-enforcement

## Instructions

# Redirect Policy NEVER_REDIRECT Enforcement

## Instructions

WHEN the TG encounters a `respond()` method that has conditional branching to decide between writing a response directly vs issuing a redirect (e.g., `shouldRenderPageAndWriteResponse()`, `shouldRedirectToTargetUrl()`, or a fallback redirect-to-buffer path), and there is a `RedirectPolicy` enum or similar policy setting that includes a `NEVER_REDIRECT` (or equivalent) policy intended to suppress redirects:

- THEN the TG should write a test that **sets the redirect policy to `RedirectPolicy.NEVER_REDIRECT`** and verifies that **regardless of other conditions**, the response is written directly and no redirect is ever issued.
- The test must simulate a **non-AJAX request** (e.g., `when(request.shouldPreserveClientUrl()).thenReturn(false)`) so that the `shouldRenderPageAndWriteResponse()` method is the first check in the `respond()` flow.
- Verify that `response.write(any(byte[].class))` is called and `response.sendRedirect(anyString())` is **never** called.
- If the policy check only appears in `shouldRenderPageAndWriteResponse()` but not in `shouldRedirectToTargetUrl()` or the fallback path, then **NEVER_REDIRECT may not be properly enforced** when those other branches are taken. The test should expose this by failing on the buggy version with an exception (e.g., `WicketRuntimeException` with message "There is no application attached to thread...") because the redirect code path proceeds to `respond()` without proper handling.

**Common pitfalls to avoid:**
- Testing only with `RedirectPolicy.ALWAYS_REDIRECT` or `AUTO_REDIRECT` but never with `NEVER_REDIRECT`.
- Only testing `NEVER_REDIRECT` under conditions where `shouldRenderPageAndWriteResponse()` returns `true` (e.g., same URL), but not under conditions where it returns `false` (e.g., different URLs) — this misses the bug where the policy isn't checked in the redirect path.
- Assuming that `NEVER_REDIRECT` checked in one branching method is sufficient to prevent redirects in all code paths of `respond()`.
- Forgetting to mock `shouldPreserveClientUrl()` returning `false`, causing `shouldRenderPageAndWriteResponse()` to return `true` and masks the bug.

### Correct Example (catches the bug):
```java
@Test
public void testRedirectPolicyNever()
{
    PageRenderer renderer = new TestPageRenderer(handler)
    {
        @Override
        protected RedirectPolicy getRedirectPolicy()
        {
            return RedirectPolicy.NEVER_REDIRECT;
        }
    };

    when(urlRenderer.getBaseUrl()).thenReturn(Url.parse("base"));
    when(requestCycle.mapUrlFor(eq(handler))).thenReturn(Url.parse("base/a"));
    when(request.shouldPreserveClientUrl()).thenReturn(false);

    renderer.respond(requestCycle);

    verify(response).write(any(byte[].class));
    verify(response, never()).sendRedirect(anyString());
}
```

### Example that misses the bug:
```java
@Test
public void testRedirectPolicyNever_sameUrls()
{
    // Only tests case where URLs are the same so shouldRenderPageAndWriteResponse returns true
    PageRenderer renderer = new TestPageRenderer(handler)
    {
        @Override
        protected RedirectPolicy getRedirectPolicy()
        {
            return RedirectPolicy.NEVER_REDIRECT;
        }
    };

    Url sameUrl = Url.parse("base");
    when(urlRenderer.getBaseUrl()).thenReturn(sameUrl);
    when(requestCycle.mapUrlFor(eq(handler))).thenReturn(sameUrl);
    when(request.shouldPreserveClientUrl()).thenReturn(false);

    renderer.respond(requestCycle);

    // This passes even in the buggy version because same URLs
    // goes through shouldRenderPageAndWriteResponse which checks the policy
    verify(response).write(any(byte[].class));
    verify(response, never()).sendRedirect(anyString());
}
```