---
name: intercept-data-cleared-after-read
description: When a request interceptor stores session metadata for redirect-after-login,
  the intercept data must be cleared after being consumed by a successful redirect.
  Without clearing, a subsequent direct visit to the login page incorrectly reuses
  stale redirect data. Use this skill to test that interception metadata is properly
  consumed and cleared after a single use.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# intercept-data-cleared-after-read

## Instructions

# Intercept Data Must Be Cleared After Successful Redirect

## Instructions

- WHEN the TG encounters a class that stores interceptor metadata in the session (e.g., `RestartResponseAtInterceptPageException.InterceptData` with `setMetaData`/`getMetaData`), and there is a method like `continueToOriginalDestination()` that consumes this data to redirect the user back to their original destination
- THEN the TG MUST write a test that verifies the intercept data is cleared after a single successful consumption. Specifically:
  1. Navigate first to a protected page (e.g., `SecurePage`) that throws a `RestartResponseAtInterceptPageException` — this should redirect to a login page and store the original destination URL in the session metadata.
  2. Submit the login form (which calls `continueToOriginalDestination()`) and verify the original protected page is rendered (e.g., `tester.assertRenderedPage(SecurePage.class)`).
  3. Then, navigate directly to the login page again (without going through the protected page), and submit the form.
  4. Verify that this time the user is NOT redirected to the original destination but instead goes to a default page (e.g., `tester.assertRenderedPage(SuccessPage.class)`).
- The test must assert the **precise rendered page class** on the second login — on the buggy version, the stale intercept data causes `continueToOriginalDestination()` to redirect again to the old protected page instead of falling through to the default page.
- Common pitfalls:
  - Testing only the first interception (protected → login → protected) without testing the second login after the intercept data should have been cleared.
  - Using the same FormTester instance for both form submissions; create separate `FormTester` instances.
  - Forgetting that `continueToOriginalDestination()` throws a restart exception, which means the fallback `setResponsePage(SuccessPage.class)` only executes if there is no original destination.

### Correct example (triggers bug):
```java
// First: go to protected page -> redirected to login
tester.startPage(SecurePage.class);
tester.assertRenderedPage(LoginPage.class);

// Submit login form -> continueToOriginalDestination() -> back to SecurePage
FormTester formTester = tester.newFormTester("form");
formTester.submit();
tester.assertRenderedPage(SecurePage.class);

// Second: go directly to login page (no interception this time)
tester.startPage(LoginPage.class);
FormTester formTester2 = tester.newFormTester("form");
formTester2.submit();

// Buggy: assertRenderedPage(SecurePage.class)  <-- STALE redirect data reused!
// Fixed: assertRenderedPage(SuccessPage.class)  <-- InterceptData cleared, falls through
tester.assertRenderedPage(SuccessPage.class);
```

### Incorrect example (fails to catch bug):
```java
// Only tests the first interception, never tests the second direct login
tester.startPage(SecurePage.class);
tester.assertRenderedPage(LoginPage.class);
FormTester formTester = tester.newFormTester("form");
formTester.submit();
tester.assertRenderedPage(SecurePage.class);
// Missing: second login that would reveal stale InterceptData
```