---
name: exception-settings-test-strategy
description: WHEN testing exception handling code that uses configurable display strategies
  (SHOW_EXCEPTION_PAGE, SHOW_INTERNAL_ERROR_PAGE, SHOW_NO_EXCEPTION_PAGE), THEN the
  TG should verify each configuration branch is reached and returns the correct handler.
  This skill helps catch bugs where configuration code paths are untested or dead
  code.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- EXCEPTION_SETTINGS_CONFIGURATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# exception-settings-test-strategy

## Instructions

# Exception Settings Configuration Strategy Testing

## Instructions

### WHEN you encounter exception handling code that switches behavior based on configurable settings/strategies (e.g., `UnexpectedExceptionDisplay` enum values, error handling strategies stored in mutable settings objects):

- **THEN** write state-based tests that configure EACH possible setting value, trigger the handler, and assert the correct response/behavior for each configuration.

- **THEN** use dependency injection or setters to configure the settings object before invoking the method under test. For example, call `application.getExceptionSettings().setUnexpectedExceptionDisplay(...)` with each enum value.

- **THEN** verify that the test produces the expected outcome for EACH setting:
  - For `SHOW_EXCEPTION_PAGE`: expect a `RenderPageRequestHandler` wrapping an `ExceptionErrorPage`
  - For `SHOW_INTERNAL_ERROR_PAGE`: expect a `RenderPageRequestHandler` wrapping the configured internal error page
  - For `SHOW_NO_EXCEPTION_PAGE`: expect an `ErrorCodeRequestHandler` with status 500 (HttpServletResponse.SC_INTERNAL_SERVER_ERROR)

- **THEN** test the default configuration as well as the configured one — the default (`SHOW_EXCEPTION_PAGE`) might behave differently than the overridden value.

- **THEN** for test methods that trigger a bug through page rendering (e.g., submitting a form that throws `RuntimeException`), set `tester.setExposeExceptions(false)` to prevent the test framework from re-throwing the exception, and use `tester.submitForm(...)` followed by `tester.getLastResponse().getStatus()` to check the HTTP response code.

- **Common pitfalls to avoid**:
  - Testing only one configuration value (e.g., only the default, or only one custom setting)
  - Forgetting to set `tester.setExposeExceptions(false)` when testing server-side error handling — without this, the exception is re-thrown and you never see the mapped error page
  - Not destroying the tester after each test (`tester.destroy()`)
  - Testing only the happy path (expected exceptions) without also testing unexpected exception handling
  - Assuming the default configuration is sufficient to cover all branches

### Example (Correct):

```java
@Test
public void showNoExceptionPage()
{
    // Configure the application to show no exception page
    tester.getApplication().getExceptionSettings()
        .setUnexpectedExceptionDisplay(ExceptionSettings.SHOW_NO_EXCEPTION_PAGE);
    tester.setExposeExceptions(false);

    ShowNoExceptionPage page = new ShowNoExceptionPage(null);
    tester.startPage(page);
    tester.submitForm("form");

    // Expect HTTP 500 because no error page is shown
    Assert.assertEquals(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, 
        tester.getLastResponse().getStatus());
}

@Test
public void showExceptionPage()
{
    // Use default configuration (SHOW_EXCEPTION_PAGE)
    tester.getApplication().getExceptionSettings()
        .setUnexpectedExceptionDisplay(ExceptionSettings.SHOW_EXCEPTION_PAGE);
    tester.setExposeExceptions(false);

    ShowNoExceptionPage page = new ShowNoExceptionPage(null);
    tester.startPage(page);
    tester.submitForm("form");

    // Expect to see the ExceptionErrorPage, not a 500
    Assert.assertNotEquals(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
        tester.getLastResponse().getStatus());
}
```

### Example (Incorrect — misses the bug):

```java
// BAD: Only tests with default settings, doesn't verify SHOW_NO_EXCEPTION_PAGE
@Test
public void showExceptionPage()
{
    tester.setExposeExceptions(false);
    // Without configuring, the default SHOW_EXCEPTION_PAGE is used
    // This test would never catch a bug in the SHOW_NO_EXCEPTION_PAGE branch
    ShowNoExceptionPage page = new ShowNoExceptionPage(null);
    tester.startPage(page);
    tester.submitForm("form");
    Assert.assertEquals(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
        tester.getLastResponse().getStatus()); // Wrong assumption!
}
```