---
name: response-type-cast-in-behavior-lifecycle
description: When a Behavior overrides beforeRender/afterRender to wrap the response,
  the TG must test that it works with all response types (especially AjaxRequestTarget's
  inner AjaxResponse), not just WebResponse. Direct casts to WebResponse without instanceof
  checks cause ClassCastException.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# response-type-cast-in-behavior-lifecycle

## Instructions

# Response Type Cast in Behavior Lifecycle

## Instructions

- WHEN the TG encounters a `Behavior` that captures and manipulates the `Response` object from `RequestCycle.get().getResponse()` in `beforeRender()` or `afterRender()`, especially by casting it to a concrete response type like `WebResponse`
- THEN the TG must write a test that triggers the behavior during an **Ajax request** (not just a normal page render), because during Ajax requests the response object may be `AjaxRequestTarget.AjaxResponse` (an inner class of `AjaxRequestTarget`), which is NOT a `WebResponse`, and a direct cast `(WebResponse) requestCycle.getResponse()` will throw `ClassCastException`
- The test should:
  1. Create a page that uses `AjaxLink` (or similar Ajax behavior) to trigger an Ajax roundtrip
  2. Add an `AbstractTransformerBehavior` (or any behavior that does response wrapping) to a component that gets updated via `target.add(component)` during the Ajax call
  3. On the buggy version, expect a `ClassCastException: org.apache.wicket.ajax.AjaxRequestTarget$AjaxResponse cannot be cast to org.apache.wicket.request.http.WebResponse` during the Ajax response rendering
- Common pitfalls to avoid:
  - Testing **only** normal (non-Ajax) page render requests — the bug only manifests during Ajax responses
  - Forgetting to use `tester.clickLink("...", true)` (the `true` parameter enables Ajax) when using WicketTester
  - Assuming the `Response` object is always a `WebResponse` or that `instanceof WebResponse` checks (which already exist) are sufficient — the problem is that the code does NOT use `instanceof` before casting in all places, e.g., `(WebResponse) ((originalResponse instanceof WebResponse) ? originalResponse : null)` is only done in `beforeRender`, but in `afterRender` the `BufferedWebResponse` cast `(BufferedWebResponse)requestCycle.getResponse()` can fail if the response was replaced by an `AjaxRequestTarget`'s internal response during rendering

### Example (correct test):

```java
@Test
public void transformationInAjaxRequest()
{
    tester.startPage(new AjaxTestPage());
    tester.assertRenderedPage(AjaxTestPage.class);

    // Trigger an Ajax request that updates a component with the transformer behavior
    tester.clickLink("updateLabel", true);
    
    // On the fixed version, the page should render the transformed content
    tester.assertContains("ajax request");
    tester.assertContainsNot("normal request");
    // On the buggy version, this would throw ClassCastException
}
```

### Example (incorrect test — misses the bug):

```java
@Test
public void responseTransformation()
{
    // This only tests a normal request, not an Ajax request
    // It will pass even on the buggy version
    TestPage testPage = new TestPage();
    testPage.add(new AbstractTransformerBehavior() { ... });
    tester.startPage(testPage);
    assertTrue(tester.getLastResponseAsString().contains("replacement"));
}
```