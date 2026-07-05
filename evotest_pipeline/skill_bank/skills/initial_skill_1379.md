---
name: raw-input-keeps-selection-across-render
description: When a Select component receives raw input during form submission with
  validation errors, the isSelected() method must check raw input even after re-render.
  Use this skill when testing form components that preserve selection state through
  raw input when validation fails.
code_tags:
- rawInput
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# raw-input-keeps-selection-across-render

## Instructions

# Raw Input Preserves Selection Across Re-render

## Instructions

- WHEN the TG encounters a `Select<T>` component (from `org.apache.wicket.extensions.markup.html.form.select`) whose `isSelected(SelectOption<?>)` method checks `hasRawInput()` to determine selection state
- THEN the TG should write a test that:
  1. Creates a page with a `Select<String>` (model type `Model<String>`) and at least 3 `SelectOption` components (e.g., with values "OPTION_0", "OPTION_1", "OPTION_2")
  2. Also includes a `required` `TextField<String>` on the same `Form` to trigger a validation error
  3. Sets a request parameter for the select ("select" -> the value of one option, e.g. `page.option1.getValue()`)
  4. Submits the form (which fails validation due to the required text field being empty)
  5. Verifies `page.form.hasError()` is true
  6. Verifies `page.select.isSelected(page.option1)` is true while raw input exists
  7. Re-starts the page (`tester.startPage(page)`) and again verifies `page.select.isSelected(page.option1)` is true — confirming the selection survives re-render via raw input
  8. Finally, submits again with both the select parameter and the text parameter ("text" -> "text is required") so validation passes, then verifies `page.select.hasRawInput()` is false and `page.select.isSelected(page.option1)` is still true (now backed by model, not raw input)

- Common pitfalls to avoid:
  - **Testing only model-backed selection**: Without raw input (validation errors), `isSelected()` falls through to model comparison. The bug is that the selection must be preserved through raw input even after re-render when the form is in error state.
  - **Forgetting to re-start the page**: The raw input must survive a page re-render (`tester.startPage(page)`) — testing only the first submit doesn't fully exercise the bug.
  - **Testing without a required field**: Without a validation error on the form, `updateModel()` would be called and the selection would be model-backed, masking the raw input path.
  - **Not checking `hasRawInput()` eventually becomes false**: After a successful submit (no validation errors), `hasRawInput()` must be false and the selection must be model-backed.

### Correct example:
```java
// WICKET-4276
@Test
public void rawInputKeepsSelectionOnError() throws Exception
{
    SelectTestPage page = new SelectTestPage();
    tester.startPage(page);
    tester.getRequest().setParameter("select", page.option1.getValue());
    tester.submitForm(page.form);
    
    // form has error ...
    assertTrue(page.form.hasError());
    // ... but option1 is selected anyway through rawInput
    assertTrue(page.select.isSelected(page.option1));
    
    tester.startPage(page);
    // ... even after re-render
    assertTrue(page.select.isSelected(page.option1));
    
    tester.getRequest().setParameter("select", page.option1.getValue());
    tester.getRequest().setParameter("text", "text is required");
    tester.submitForm(page.form);
    
    // ... until successful submit without rawInput
    assertFalse(page.select.hasRawInput());
    assertTrue(page.select.isSelected(page.option1));
}
```

### Incorrect example (missing re-render check):
```java
@Test
public void rawInputKeepsSelectionOnError_incomplete() throws Exception
{
    SelectTestPage page = new SelectTestPage();
    tester.startPage(page);
    tester.getRequest().setParameter("select", page.option1.getValue());
    tester.submitForm(page.form);
    
    // Only checks after first submit, misses the re-render scenario
    assertTrue(page.form.hasError());
    assertTrue(page.select.isSelected(page.option1));
    
    // Missing: tester.startPage(page); and re-check
    // Missing: successful submit to verify hasRawInput() becomes false
}
```