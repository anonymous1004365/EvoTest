---
name: ajax-choice-group-validation-on-nested-error
description: When an AjaxFormChoiceComponentUpdatingBehavior triggers on a RadioGroup/CheckGroup,
  validation errors on nested FormComponents should prevent the group from being marked
  valid. Tests must verify that the group stays invalid and its model object remains
  unchanged when a nested child has an error.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# ajax-choice-group-validation-on-nested-error

## Instructions

# Ajax Choice Group Validation on Nested Error

## Instructions

- WHEN the TG encounters an `AjaxFormChoiceComponentUpdatingBehavior` attached to a `RadioGroup` or `CheckGroup` that contains nested `FormComponent`s (e.g. `TextField` with `setRequired(true)`)
- THEN the TG should write a test that:
  1. Submits the form (to trigger validation on the nested component, creating an error message on it)
  2. Executes an AJAX event (e.g. `"click"`) on the group via `tester.executeAjaxEvent(component, "click")` with a request parameter like `"form.group"` set to a radio button's value (e.g. `page.radioFalse.getValue()`)
  3. Asserts that the group component is **not valid** (`assertFalse(page.group.isValid())`) — even though the radio selection itself is valid, because the nested child still has a validation error
  4. Asserts that the group's model object stays unchanged (e.g. `assertEquals(Boolean.TRUE, page.group.getModelObject())`) — the model should NOT be updated because the group is invalid overall

  The bug occurs because `onEvent()` in `AjaxFormComponentUpdatingBehavior` only validates the attached form component itself, not its nested children. When the behavior calls `formComponent.validate()`, the `RadioGroup`'s own validation passes, and via `getUpdateModel()` the model gets updated — but the nested `TextField`'s error message should have made the whole group invalid. The fix ensures that the group remains invalid and the model is not updated when nested children have errors.

- Include what to verify: check `hasErrorMessage()` on the nested component, check `isValid()` on the group, check the group's model object value after the AJAX event
- Common pitfalls to avoid:
  - ❌ Testing only the radio selection value change without setting up a nested component that produces a validation error (e.g. a required `TextField` left empty)
  - ❌ Asserting the group's model object was updated to the new radio value when it should remain unchanged
  - ❌ Forgetting to submit the form first to trigger the nested component's validation/error message before executing the AJAX event
  - ❌ Testing only with `RadioGroup` but not considering `CheckGroup` which has the same behavior

### Correct Example
```java
// Prepare: submit form to trigger nested validation error
tester.submitForm(page.form);
assertTrue(page.text.hasErrorMessage());

// Execute AJAX event on the group with a parameter for radioFalse
tester.getRequest().setParameter("form.group", page.radioFalse.getValue());
tester.executeAjaxEvent(page.group, "click");

// Group should remain invalid because nested text has error
assertFalse(page.group.isValid());
// Model object stays unchanged
assertEquals(Boolean.TRUE, page.group.getModelObject());
```

### Incorrect Example
```java
// ❌ Wrong: Doesn't submit form first, so nested component has no error
tester.getRequest().setParameter("form.group", page.radioFalse.getValue());
tester.executeAjaxEvent(page.group, "click");

// ❌ Wrong: Asserts model was updated to false (the new selection)
assertEquals(Boolean.FALSE, page.group.getModelObject());
// ❌ The group passes validation only because nested error wasn't triggered
```