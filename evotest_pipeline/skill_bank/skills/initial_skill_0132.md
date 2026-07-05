---
name: intercept-page-header-validation-guard
description: WHEN the code uses RestartResponseAtInterceptPageException (or similar
  render-interruption mechanisms) and has post-render validation logic like validateHeaders()
  in WebPage.onAfterRender(), THEN test that validation is skipped when the page's
  rendering was intercepted. This prevents false-positive missing-header errors from
  being reported for pages that never finished rendering.
code_tags:
- INTERRUPTED_RENDER_GUARD
test_pattern: STATE_TEST
---

# intercept-page-header-validation-guard

## Instructions

# Intercept Page Header Validation Guard

## Instructions

WHEN the code contains a render lifecycle with post-render validation (e.g., `validateHeaders()` called in `WebPage.onAfterRender()`) AND uses a render-interrupting mechanism like `RestartResponseAtInterceptPageException`:

- THEN write a test that creates a page which throws `RestartResponseAtInterceptPageException` during `onInitialize()` (before rendering completes)
- THEN verify that any post-render validation logic (e.g., `reportMissingHead()`, `validateHeaders()`) is NOT invoked when the page's rendering was interrupted
- THEN use `WicketTestCase` and `tester.startPage()` to render the page through the framework, so the full lifecycle (`onInitialize()` → `onRender()` → `onAfterRender()`) executes naturally
- THEN use a flag (e.g., `AtomicBoolean` or a boolean field) inside an overridden validation callback (e.g., `reportMissingHead(CharSequence)`) to assert that it was NOT called — call `fail(...)` if it IS called unexpectedly
- THEN verify the actual page rendered (e.g., `tester.assertRenderedPage(RedirectPage.class)` or the intercept target page) which confirms the interception worked and the validation was correctly bypassed

**Common pitfalls to avoid:**
- Testing only the happy-path (fully-rendered page) and missing the interrupt-path where validation should be skipped
- Assuming header validation check (`wasRendered(this)`) is sufficient without actually verifying it works when an exception interrupts rendering
- Using a simple mock or stub that bypasses the real `RestartResponseAtInterceptPageException` stack throwing mechanism — the test must actually throw the exception during page initialization so the rendering lifecycle is cut short
- Forgetting to add header contributors (e.g., `CoreLibrariesContributor.contribute()`) to make the test realistic — without them, `reportMissingHead` would never be triggered anyway

**Correct example (from code):**
```java
@Test
public void interceptedRenderDoesNotReportMissingHeader()
{
    tester.startPage(new MockHomePage()
    {
        @Override
        protected void onInitialize()
        {
            throw new RestartResponseAtInterceptPageException(getApplication().getHomePage());
        }

        @Override
        public void renderHead(IHeaderResponse response)
        {
            super.renderHead(response);
            CoreLibrariesContributor.contribute(getApplication(), response);
        }

        @Override
        protected void reportMissingHead(CharSequence collectedHeaderOutput)
        {
            fail("missing headers should not be reported when rendering was intercepted");
        }
    });
}
```

**Incorrect example (missing the interrupt):**
```java
// WRONG: only tests happy-path, never verifies that intercepted rendering skips validation
@Test
public void testHeaderValidation()
{
    NoHeadNoBodyPage page = new NoHeadNoBodyPage();
    tester.startPage(page);
    // This only proves validation works when rendering completes, not that it's skipped on interception
}
```