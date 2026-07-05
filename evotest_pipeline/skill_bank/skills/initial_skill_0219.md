---
name: validation-error-feedback-toString-comparison
description: When testing feedback message filtering, format, or comparison logic
  in Wicket, verify that messages returned by feedback collectors are compared by
  their message string value, not by their toString() representation which may include
  wrapper object details.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
- TOSTRING_OVERLOAD
test_pattern: STATE_TEST
---

# validation-error-feedback-toString-comparison

## Instructions

# ValidationErrorFeedback toString() Comparison Bug

## Instructions

- WHEN the TG is testing a feedback message filtering, matching, or assertion method — such as `WicketTester.assertFeedback()` or custom `FeedbackMessageFilter` implementations — that compares feedback messages by calling `toString()` on them
- THEN the TG should verify that:
  1. The method under test does NOT rely on the `toString()` representation of `ValidationErrorFeedback` objects for comparison. `ValidationErrorFeedback.toString()` returns a string like `"ValidationErrorFeedback{message=wrong email address pattern for email}"` which includes class name and wrapper details, NOT just the plain message `"wrong email address pattern for email"`.
  2. A test that compares using `toString()` will fail on the buggy version with a mismatch like `expected:<[wrong email address pattern for email]> but was:<[ValidationErrorFeedback{message=wrong email address pattern for email}]>`.
  3. The correct approach is to compare the `getMessage()` value of the feedback message, or to use the proper feedback assertion API that internally extracts the message string.

- The TG should include a state-verification test that:
  - Creates a `ValidationErrorFeedback` with a known message string.
  - Calls `toString()` on it and asserts the result is NOT equal to the plain message string (confirming the buggy behavior pattern).
  - If testing the fix, verifies that the feedback system extracts the message correctly (e.g., via `getMessage()`).

- Common pitfalls to avoid:
  - ❌ Using `assertEquals("some message", feedbackMessage.toString())` — this will fail because `toString()` returns `"ValidationErrorFeedback{message=some message}"`.
  - ❌ Assuming `toString()` on a feedback message returns a plain error string.
  - ✅ Using `assertEquals("some message", ((ValidationErrorFeedback) feedbackMessage).getMessage())` — this correctly extracts the plain message.
  - ✅ If the test compares expected vs actual strings using the feedback system's report method, make sure the system doesn't use `toString()` internally.

- Concrete example (buggy test):
  ```java
  // This test FAILS on buggy version — toString() returns wrapper object, not plain message
  String feedback = tester.getFeedbackMessages("form").toString();
  assertEquals("wrong email address pattern for email", feedback);
  ```

- Concrete example (fixed test):
  ```java
  // This test PASSES — it extracts the actual message value
  List<Serializable> messages = tester.getFeedbackMessages("form");
  assertEquals(1, messages.size());
  ValidationErrorFeedback vef = (ValidationErrorFeedback) messages.get(0);
  assertEquals("wrong email address pattern for email", vef.getMessage());
  ```