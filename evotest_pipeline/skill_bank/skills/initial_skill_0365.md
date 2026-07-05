---
name: disabled-form-component-validation-skip
description: WHEN a form has FormComponent instances that are disabled or invisible
  but still carry validation error messages, THEN tests should verify that onSubmit()
  is called despite the errors on disabled/invisible components. The form should skip
  validation of non-visible and non-enabled form components.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- DISABLED_FORM_COMPONENT_VALIDATION
- VALIDATION
test_pattern: STATE_TEST
---

# disabled-form-component-validation-skip

## Instructions

# Disabled Form Component Validation Skipping

## Instructions

WHEN the TG encounters a `Form` containing `FormComponent` instances (e.g., `TextField`) whose `setEnabled(false)` or `setVisible(false)` has been called after validation errors accumulated on them, THEN the TG should write a test that:

1. Creates a `Form` with a `TextField` that has `setRequired(true)` (or any validator that makes it invalid when empty).
2. Submits the form while the component is still enabled and visible, and verifies that `onError()` was called and `onSubmit()` was NOT called, and that `field1.hasErrorMessage()` returns `true`.
3. Then calls `field1.setEnabled(false)` (or `setVisible(false)`) to disable/hide the component.
4. Submits the form again, and verifies that `onSubmit()` IS called and `onError()` is NOT called, even though `field1.hasErrorMessage()` still returns `true`.

The bug is that when a `FormComponent` is disabled (`isEnabledInHierarchy()` returns `false`) or invisible (`isVisibleInHierarchy()` returns `false`), the `Form` should skip it during validation — but the form should still submit successfully despite previous error messages remaining on those skipped components.

Use `AtomicBoolean` flags in the test page to track `onSubmit()` and `onError()` calls. Use `FormTester` from `wicket-core` to simulate submissions.

Common pitfalls to avoid:

- **Testing only the enabled/visible case**: The TG might test form submission only with visible, enabled components. They MUST also test the disabled/invisible scenario.
- **Clearing error messages before submitting**: The TG might clear feedback messages before the second submit. This is unnecessary — the test should verify that the form submits WITH the old error messages still present on the disabled component.
- **Expecting `onError()` to be called on the second submit**: The whole point of the fix is that disabled/invisible components' validation errors should not block form submission.
- **Using `setVisible(false)` on the form itself instead of the component**: Disabling/hiding the form would skip ALL validation, which is a different scenario. The component itself must be disabled/hidden.

### Correct example (Java/JUnit 4 with WicketTester):

```java
@Test
public void formSubmitsEvenWithInvalidButDisabledFormComponent()
{
    TestPage page = tester.startPage(TestPage.class);
    assertFalse(page.onSubmitCalled.get());
    assertFalse(page.onErrorCalled.get());

    // First submit: component is enabled and visible -> validation fails
    FormTester formTester = tester.newFormTester(page.form.getPageRelativePath());
    formTester.submit();
    assertTrue(page.field1.hasErrorMessage());
    assertFalse(page.onSubmitCalled.get());
    assertTrue(page.onErrorCalled.get());
    page.onErrorCalled.set(false);

    // Disable the component and submit again
    page.field1.setEnabled(false);
    formTester = tester.newFormTester(page.form.getPageRelativePath());
    formTester.submit();
    assertTrue(page.field1.hasErrorMessage());  // error still present
    assertTrue(page.onSubmitCalled.get());       // form submits successfully
    assertFalse(page.onErrorCalled.get());       // onError is NOT called
}
```

### Incorrect example:

```java
@Test
public void formSubmitsEvenWithInvalidButDisabledFormComponent()
{
    TestPage page = tester.startPage(TestPage.class);
    page.field1.setEnabled(false);
    FormTester formTester = tester.newFormTester(page.form.getPageRelativePath());
    formTester.submit();
    // BUG: Without first submitting while enabled, field1 has no error message.
    // This doesn't test that EXISTING errors on disabled components are ignored.
    // The test passes even on the buggy version because no error was ever set.
    assertTrue(page.onSubmitCalled.get());
}
```

For the test page setup, use a pattern like this:

```java
public static class TestPage extends WebPage implements IMarkupResourceStreamProvider
{
    public final AtomicBoolean onSubmitCalled = new AtomicBoolean(false);
    public final AtomicBoolean onErrorCalled = new AtomicBoolean(false);
    public final TextField<String> field1;
    public final Form<?> form;

    public TestPage()
    {
        form = new Form<Void>("form")
        {
            @Override
            protected void onSubmit() { onSubmitCalled.set(true); }
            @Override
            protected void onError() { onErrorCalled.set(true); }
        };
        add(form);
        form.add(field1 = new TextField<>("field1", Model.of("")));
        field1.setRequired(true);
    }

    @Override
    public IResourceStream getMarkupResourceStream(MarkupContainer container, Class<?> containerClass)
    {
        return new StringResourceStream(
            "<html><body><form wicket:id='form'><input wicket:id='field1' type='text'/></form></body></html>");
    }
}
```