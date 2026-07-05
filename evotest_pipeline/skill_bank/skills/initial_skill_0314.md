---
name: form-tester-email-validation
description: When testing form submission with validators (like EmailAddressValidator),
  the test must use both valid and invalid input values to verify validation properly
  catches errors. This skill helps write tests that exercise the validator's rejection
  path.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# form-tester-email-validation

## Instructions

# Form Tester Email Address Validation

## Instructions

- WHEN the TG encounters a form submission test that uses FormTester.setValue() to populate a form field that has an attached validator (e.g., EmailAddressValidator, PatternValidator, or any IValidator)
- THEN the TG should write a test that submits the form with **invalid input values** that should be rejected by the validator, and verify that validation errors are reported
- Specifically:
  - For EmailAddressValidator, use an invalid email like `"invalid-email"` (no @ sign) as a test value
  - After calling form.setValue(fieldPath, invalidValue) and form.submit(), assert that the form has validation errors by checking that `form.hasError()` returns true or that the error feedback panel displays an error message
  - The test should verify the validator **rejects** bad input, not just accepts good input
- Common pitfalls:
  - **Only testing valid input** and assuming validation works — this misses the bug where validation errors are swallowed or not properly detected
  - **Not checking the form's error state** after submitting invalid data — assertions on success path only are insufficient
  - **Assuming FormTester processes validators** — the bug may be that FormTester's form submission does not properly trigger validator validation

### Correct Example (Catches the Bug)

```java
// FormTesterTest.java - tests EmailAddressValidator rejection
public void test_1() throws Exception {
    WicketTester tester = new WicketTester();
    tester.startPage(EmailPage.class);
    FormTester form = tester.newFormTester("form");
    form.setValue("email", "invalid-email"); // no @ sign, should fail validation
    form.submit();
    assertTrue("Form should have validation errors for invalid email", form.hasError());
}
```

### Incorrect Example (Misses the Bug)

```java
// Only tests valid input, never exercises the validation rejection path
public void test_1() throws Exception {
    WicketTester tester = new WicketTester();
    tester.startPage(EmailPage.class);
    FormTester form = tester.newFormTester("form");
    form.setValue("email", "user@example.com"); // valid email — no error expected
    form.submit();
    // No assertion about form errors — misses the bug entirely
}
```