---
name: exception-after-response-commit
description: When a response throws an exception after headers have been committed
  (e.g., during after-render), the error handler must preserve the original error
  status. This skill teaches testing that a sendError (e.g., 500) with no-cache headers
  is correctly set even when an exception occurs late in the response lifecycle.
code_tags:
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# exception-after-response-commit

## Instructions

# Exception After Response Commit

## Instructions

- WHEN the TG encounters code where an HTTP response can throw an exception after the response buffer has already been committed (e.g., in `onAfterRender()`, `afterDelivery()`, or any lifecycle hook that runs after headers/status are set), and the framework catches this exception in an error handler that calls `sendError(int sc, String msg)` or `setStatus(int sc)`
- THEN the TG should test that when an exception occurs after the response has started flushing/committing, the error handler still properly sets the HTTP status code (e.g., 500) and does not overwrite already-written data with an error page that the client would misinterpret.
  - The test should verify that the last response status is `500` (via `tester.getLastResponse().getStatus()`)
  - The test should configure: `REDIRECT_TO_BUFFER` render strategy (so responses are buffered) and `SHOW_EXCEPTION_PAGE` for unexpected exception display
  - The test should use an `AjaxLink` (or similar) that triggers an exception during `onAfterRender()` (not in `onClick()` itself)
- Common pitfalls:
  - ❌ Testing only the exception in `onClick()` — the bug manifests when the exception occurs in `onAfterRender()` AFTER the component was added to the target (i.e., after `target.add(this)`), causing the response buffer to already contain headers/data
  - ❌ Forgetting to set `tester.setExposeExceptions(false)` before triggering the event, which would cause the test to throw the exception directly instead of testing the error handling path
  - ❌ Testing only with a standard (non-buffered) render strategy, missing the scenario where REDIRECT_TO_BUFFER is active

### Correct example (this test catches the bug):
```java
@Test
public void bufferedExceptionErrorPage()
{
    tester.getApplication()
        .getRequestCycleSettings()
        .setRenderStrategy(RequestCycleSettings.RenderStrategy.REDIRECT_TO_BUFFER);
    tester.getApplication()
        .getExceptionSettings()
        .setUnexpectedExceptionDisplay(ExceptionSettings.SHOW_EXCEPTION_PAGE);
    internalErrorPage();
}

@Test
public void internalErrorPage()
{
    tester.startPage(TestErrorPage.class);  // contains AjaxLink that throws in onAfterRender after target.add(this)
    tester.setExposeExceptions(false);
    AjaxLink<?> link = (AjaxLink<?>)tester.getComponentFromLastRenderedPage("link");
    tester.executeAjaxEvent(link, "click");
    assertEquals(500, tester.getLastResponse().getStatus());
}
```

### Incorrect example (would NOT catch this bug):
```java
// WRONG: Tests only the non-buffered path (missing REDIRECT_TO_BUFFER)
@Test
public void exceptionErrorPage()
{
    tester.getApplication()
        .getExceptionSettings()
        .setUnexpectedExceptionDisplay(ExceptionSettings.SHOW_EXCEPTION_PAGE);
    tester.startPage(TestErrorPage.class);
    tester.setExposeExceptions(false);
    AjaxLink<?> link = (AjaxLink<?>)tester.getComponentFromLastRenderedPage("link");
    tester.executeAjaxEvent(link, "click");
    assertEquals(500, tester.getLastResponse().getStatus()); // may pass but misses the buffered scenario
}
```

### Key insight
The bug occurs because in the REDIRECT_TO_BUFFER strategy, the response is committed before the error page is rendered. When `sendError()` is called on an already-committed `HttpServletResponse`, it is ignored by the servlet container (or throws `IllegalStateException`). The fix likely involves checking `response.isCommitted()` before calling `sendError()` and instead writing the error content directly to the already-committed stream. The test must trigger an `onAfterRender()` exception (not `onClick()`) because that's when headers/data have already been flushed to the buffer.