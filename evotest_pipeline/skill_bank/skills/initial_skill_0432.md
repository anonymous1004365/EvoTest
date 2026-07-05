---
name: component-type-hierarchy-event-name-check
description: WHEN the TG encounters behavior code that checks `instanceof TextField`
  or `instanceof TextArea` to conditionally set event names (e.g., 'inputchange' vs
  'change'), THEN it should test with subclasses of TextField/TextArea to verify the
  type check is inclusive enough, and verify the rendered Ajax event name in the expected
  HTML output to ensure the correct event binding.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- EVENT_NAME_CONFIGURATION
- AJAX_BEHAVIOR_SETUP
test_pattern: PARAMETRIC_TEST
---

# component-type-hierarchy-event-name-check

## Instructions

# Component Type Hierarchy Event Name Check

## Instructions

- WHEN the source code contains a conditional check using `instanceof TextField` or `instanceof TextArea` to determine which Ajax event name to set on `AjaxRequestAttributes` (e.g., setting 'inputchange' for text components and 'change' for others)
- THEN the TG should create a test that uses a **subclass of TextField or TextArea** (not the exact class) to verify that the `instanceof` check correctly handles the type hierarchy. For example, use a custom subclass like `class MyTextField extends TextField<String> { ... }` and attach the behavior to it.
- The test should render the page and verify the **Ajax event name** in the rendered HTML output. The expected output should contain the correct event name (e.g., `"e":"inputchange change"` for text input components, or `"e":"change"` for non-text components like `DropDownChoice`).
- Use `WicketTester.executeTest(TestPage.class, "expected.html")` to compare the full rendered output against a baseline file, ensuring the Ajax binding includes the right event name.
- **Common pitfalls to avoid:**
  - Testing only the exact `TextField` or `TextArea` class, missing the case where subclasses behave differently.
  - Forgetting to verify the actual rendered Ajax event binding string (e.g., `"e":"inputchange change"`) in the HTML output.
  - Assuming the behavior works for all component types without testing at least one text subclass and one non-text component (e.g., `DropDownChoice`).

### Example (Correct test approach)

```java
// Test page with a TextField subclass and a DropDownChoice
public class OnChangeAjaxBehaviorTestPage extends WebPage {
    public OnChangeAjaxBehaviorTestPage() {
        Form<Void> form = new Form<>("form");
        add(form);

        // Custom subclass of TextField
        class CustomTextField extends TextField<String> {
            CustomTextField(String id) { super(id); }
        }
        TextField<String> field = new CustomTextField("field");
        field.add(new OnChangeAjaxBehavior() {
            @Override protected void onUpdate(AjaxRequestTarget target) {}
        });
        form.add(field);

        // Non-text component
        DropDownChoice<?> choice = new DropDownChoice<>("dropDown");
        choice.add(new OnChangeAjaxBehavior() {
            @Override protected void onUpdate(AjaxRequestTarget target) {}
        });
        form.add(choice);
    }
}

// Test method
@Test
public void rendering() throws Exception {
    tester.getSession().setLocale(Locale.ENGLISH);
    executeTest(OnChangeAjaxBehaviorTestPage.class,
        "OnChangeAjaxBehaviorTestPage_expected.html");
}

// Expected HTML snippet:
// TextField subclass: "e":"inputchange change"
// DropDownChoice:     "e":"change"
```

### Example (Incorrect approach)

```java
// WRONG: Only tests exact TextField, not a subclass
// This would miss the bug if instanceof fails for subclasses
public class OnChangeAjaxBehaviorTestPage extends WebPage {
    public OnChangeAjaxBehaviorTestPage() {
        // ...
        TextField<String> field = new TextField<>("field"); // NOT a subclass
        // ...
    }
}
```

- When the test passes on the fixed version but fails on the buggy version, the failure will appear as a mismatch in the expected HTML file where the event name (e.g., `"e":"inputchange"` instead of `"e":"inputchange change"`) is incorrect for a TextField subclass, or where `"e":"change"` appears when `"e":"inputchange change"` was expected.