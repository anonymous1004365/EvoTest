---
name: submitlink-form-submission-type-check
description: When testing form submission via SubmitLink, the TG should verify that
  submitting a form using a SubmitLink that wraps an embedded form component triggers
  the form's onSubmit. The key is that the submitter's type must be checked for IFormSubmitter,
  not just checking if a SubmitLink has a form reference.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# submitlink-form-submission-type-check

## Instructions

# SubmitLink Form Submission Type Checking

## Instructions

- WHEN the TG encounters a SubmitLink that wraps an embedded form component (e.g., a FormPage containing a Form with a SubmitLink as a child), and the SubmitLink's `onSubmit` calls `getForm().onFormSubmitted(this)`.
- THEN the TG should test that `Form.onFormSubmitted()` correctly delegates to submission processing when called with an `IFormSubmitter` that is a SubmitLink. The test must verify that when the SubmitLink is clicked via `tester.executeAjaxEvent(linkComponent, "click")`, the form's submission process is triggered. Specifically, the TG should verify that the form's `onSubmit()` is called (e.g., by checking a submitted flag or state change on the form's model object).
- Include concrete values: use `FormPage` (from `org.apache.wicket.markup.html.link.submitLink`), `SubmitLink` (from `org.apache.wicket.markup.html.form`) and check that the form's submitted flag (e.g., a `boolean submitted` field on the page) is set to `true` after the Ajax event.
- What mistakes to avoid: Do NOT assume the SubmitLink can be rendered/clicked without a proper wicket:id path in the markup (e.g., `testFormAndLinkAreSubmitted` must reference the correct component path like `"form:link"`). Do NOT forget that `tester.executeAjaxEvent` requires the component path as a string and the event type as "click" for SubmitLink.

### Correct Example:
```java
// Test that a SubmitLink inside a Form triggers form submission
tester.startPage(FormPage.class);
tester.executeAjaxEvent("form:link", "click");
FormPage page = (FormPage) tester.getLastRenderedPage();
assertTrue("Form should have been submitted", page.isFormSubmitted());
```

### Incorrect Example:
```java
// WRONG: Submits the form directly without clicking the SubmitLink
tester.startPage(FormPage.class);
Form form = (Form) tester.getComponentFromLastRenderedPage("form");
form.process();
// Never checks the SubmitLink's onClick behavior
```