---
name: disabled-state-propagation-from-group-to-checkbox
description: WHEN a CheckGroup or RadioGroup parent container is set disabled, THEN
  child Check or Radio components must also render with disabled="disabled". This
  skill teaches you to test that form component groups propagate their disabled attribute
  to all child inputs during tag rendering.
code_tags:
- NULL_CHECK
- RESOURCE_LOOKUP
- DISABLED_STATE_PROPAGATION
test_pattern: PARAMETRIC_TEST
---

# disabled-state-propagation-from-group-to-checkbox

## Instructions

# Disabled State Propagation from Group to Checkbox

## Instructions

- WHEN the TG encounters a `CheckGroup`, `RadioGroup`, or similar form component container class that manages child `Check` or `Radio` input components
- THEN the TG should verify that when the parent container is set to `disabled` state, all child checkboxes/radios inherit the `disabled="disabled"` attribute in their rendered HTML output
- Specifically, create a test page with a `CheckGroup` (or `RadioGroup`) that is disabled via `group.setEnabled(false)`, add multiple `Check` (or `Radio`) components to it, render the page, and assert that each `<input type="checkbox">` (or `<input type="radio">`) contains the `disabled="disabled"` attribute in the rendered markup
- The bug occurs when the `CheckGroup.onComponentTag()` removes the `disabled` attribute from the tag (via `tag.remove("disabled")`), which prevents child `Check` components that inherit the disabled state from the parent from rendering the attribute correctly
- Always test with at least two child inputs, as the interaction between `CheckGroup.onComponentTag()` and `Check.onComponentTag()` may affect multiple children differently (e.g., a direct child vs. a child inside a nested container)
- Compare the rendered output against an expected HTML file (e.g., `CheckGroupDisabledTestPage_expected.html`) that contains the correct `disabled="disabled"` attributes
- Common pitfalls to avoid:
  - Testing only the parent container state without verifying the rendered child component tags
  - Assuming that setting `group.setEnabled(false)` automatically propagates to child components — this must be tested explicitly
  - Using only a single child checkbox, which may miss bugs where the `disabled` attribute removal in `CheckGroup.onComponentTag()` only affects certain child rendering paths
  - Forgetting to include both the outer `<input>` elements directly under `CheckGroup` and inner ones wrapped in additional containers (like `<span wicket:id="container">`)

### Correct example
```java
// Test page with disabled CheckGroup
public class CheckGroupDisabledTestPage extends WebPage {
    public CheckGroupDisabledTestPage() {
        Form<?> form = new Form<>("form");
        add(form);
        CheckGroup<String> group = new CheckGroup<>("group", new ArrayList<String>());
        group.add(new Check<>("check1", new Model<>("check0"), group));
        WebMarkupContainer container = new WebMarkupContainer("container");
        container.add(new Check<>("check2", new Model<>("check1"), group));
        group.add(container);
        group.setEnabled(false);
        form.add(group);
    }
}
```

### Incorrect example
```java
// Missing: only testing enabled state, not disabled propagation
public class CheckGroupTest {
    @Test
    public void testCheckGroup() {
        // BUG: Only tests enabled CheckGroup, never tests disabled propagation
        executeTest(CheckGroupTestPage.class, "CheckGroupTestPage_expected.html");
    }
}
```

### What the test should assert
- The test should render the page and compare against an expected HTML file
- The expected HTML file should contain `<input type="checkbox" ... disabled="disabled">` for each child checkbox
- The test should fail on the buggy version (missing `disabled="disabled"` attribute in child checkboxes) and pass on the fixed version