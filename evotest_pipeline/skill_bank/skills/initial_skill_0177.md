---
name: feedback-message-clearing-before-validation
description: When a form's feedback messages are cleared before validation/processing,
  the hasError() check may report stale state. Teach the TG to verify that clearing
  messages between validation rounds does not affect error detection, and to test
  re-submission scenarios where feedback state and processing order matter.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- FEEDBACK_MESSAGE_CLEARING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# feedback-message-clearing-before-validation

## Instructions

# Feedback Message Clearing Before Validation

## Instructions

- WHEN the TG encounters a `Form` (or `FormComponent`) that calls `feedbackMessages.clear()` (or `clearFeedbackMessages()`) before or during `process(IFormSubmitter)` — especially when the clear is done in an override of `onSubmit()` or `onValidate()` — THEN the TG should write a test that validates the order of clearing relative to error detection.

  Specifically:
  - WHEN `clearFeedbackMessages()` is called at the start of `process()` on the form, THEN the TG should verify that `hasError()` still returns `true` when validation errors are present and have been added AFTER the clear.
  - The TG should test a scenario where:
    1. Submit the form with invalid data (e.g., empty required field).
    2. Assert `form.hasError()` returns `true`.
    3. Re-submit the form again (same invalid data) — this triggers `process()` again, which calls `clearFeedbackMessages()`.
    4. Assert `form.hasError()` returns `true` again (the error should be re-detected).
  - The test should expect that `hasError()` returns `true` after each invalid submission, even when `clearFeedbackMessages()` is called in `process()` between submissions.

- Common pitfalls to avoid:
  - Testing only the first submission and not a re-submission (which exercises the clear-then-revalidate path).
  - Assuming `hasError()` returns a persistent state — it may check `hasErrorMessage()` which depends on the feedback messages model being populated AFTER validation. If messages are cleared before validation, the old errors are gone, but new ones must be present for `hasError()` to be `true`.
  - Not checking `form.hasError()` vs `page.hasErrorMessage()`. The TG should call `form.hasError()` directly on the form component.

- Example of what the test should look like (correct):

```java
// Submit form with invalid data (empty required field)
tester.executeAjaxEvent(form, "submit");
// After first submission, errors should be present
assertTrue("Form should have errors after invalid submit", page.form.hasError());

// Re-submit with same invalid data (this triggers process() which clears and re-validates)
tester.executeAjaxEvent(form, "submit");
// After re-submission, errors should STILL be present (clear then re-validate)
assertTrue("Form should still have errors after re-submit", page.form.hasError());
```

- Example of what the test should NOT do (incorrect):

```java
// Only testing once — misses the bug
tester.executeAjaxEvent(form, "submit");
assertTrue("Form should have errors", page.form.hasError());

// No second submission — the bug only manifests on re-submission
```

- The underlying bug behavior: when `clearFeedbackMessages()` is called at the beginning of `process()`, the old feedback messages are removed BEFORE validation runs. If the validation then fails, new error messages are added. However, if the form's `hasError()` method checks `hasErrorMessage()` (which in turn checks the feedback messages model that was already populated from a previous render but not re-populated after clearing), it may return `false` even though validation errors exist. The fix ensures that after clearing and re-validating, the error state is correctly computed from the newly added error messages.