---
name: stateless-form-get-request-method-mismatch
description: When a form is submitted via GET but the form HTML uses method="post"
  (or vice versa), the StatelessForm's process() method must properly handle the mismatch.
  This skill helps test that when a stateless form receives a request with an unexpected
  HTTP method, it correctly calls onMethodMismatch() instead of proceeding with form
  processing.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# stateless-form-get-request-method-mismatch

## Instructions

# StatelessForm Method Mismatch Handling

## Instructions

- WHEN the TG encounters a `StatelessForm` that overrides the `process()` method (e.g., to capture request parameters before delegation), or a `Form` with any stateless behavior
- THEN the TG should write a test that submits the form using an HTTP method DIFFERENT from what the form expects (e.g., submitting via GET when the form uses method="post", or submitting via POST when the form uses method="get")
- The test MUST verify that `onMethodMismatch()` is invoked, and that the form does NOT proceed with normal processing (e.g., model objects are not updated, validation is not run, etc.)
- Include concrete assertions: verify that `onMethodMismatch()` returns a `MethodMismatchResponse` (e.g., `RedirectResponse`), and that the request is redirected rather than the form being processed normally
- Common pitfalls to avoid:
  - ❌ Testing only the happy path where the correct HTTP method is used
  - ❌ Assuming the form will always use POST (testing only POST requests)
  - ❌ Not testing what happens to model state after a method mismatch (it should remain unchanged)
  - ❌ Forgetting that `StatelessForm.process()` captures request parameters *before* delegating to `super.process()` — the parameter capture may succeed but the actual processing must still be blocked

### Correct Example

```java
@Test
public void testMethodMismatchOnGetRequest()
{
    // Create a stateless form that expects POST
    StatelessForm<?> form = new StatelessForm<Void>("form")
    {
        @Override
        protected MethodMismatchResponse onMethodMismatch()
        {
            return new RedirectResponse("/error");
        }
    };
    
    // Simulate a GET request to the form that expects POST
    // (e.g., by setting request method to GET in the test harness)
    
    // Submit the form
    form.process(submittingComponent);
    
    // Verify the form did NOT process normally
    // e.g., model object field was NOT updated
    assertNull(form.getModelObject());
    
    // Verify the mismatch response was triggered
    // (the request was redirected rather than processed)
}
```

### Incorrect Example

```java
@Test
public void testFormProcess()
{
    // ❌ Only tests the normal POST case
    // Does not verify what happens on GET when form expects POST
    StatelessForm<?> form = new StatelessForm<Void>("form") {};
    form.process(submittingComponent);
    // No assertion about method mismatch behavior
}
```

### What to verify on the buggy version

On the buggy version, submitting via the wrong HTTP method will incorrectly proceed with form processing (e.g., updating model objects, running validation) instead of redirecting. The test should fail on the buggy version by showing that form processing occurred despite the method mismatch.