---
name: border-body-hidden-component-use-check
description: When a Border's body container is hidden (e.g., via setHidden(true))
  but child components are added directly to the Border (not the body), the component-use-check
  debug feature may incorrectly flag these children as unused. This skill teaches
  how to test that scenario without false failures.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# border-body-hidden-component-use-check

## Instructions

# Border Body Hidden with Component-Use-Check

## Instructions

- WHEN the TG encounters a `Border` subclass with a hideable/visible body container (e.g., `HideableBorder` that wraps `getBodyContainer()` inside a `WebMarkupContainer` with toggled `isVisible()`) AND the `DebugSettings.setComponentUseCheck(true)` is enabled
- THEN the TG should write a test that adds child components **directly to the Border** (not to its body container), hides the body container (e.g., `setHidden(true)`), starts the page with `tester.startPage(page)`, and asserts the page renders successfully without any `ComponentNotFoundException` or `WicketRuntimeException` from the component-use-check logic

- **Concrete scenario from the codebase**: `HideableBorder` adds `getBodyContainer()` into a wrapper container (`containerWrapper`) whose `isVisible()` returns `!hidden`. Setting `setHidden(true)` makes the wrapper invisible. A child Label is added via `border.add(new Label("content", "label"))` — i.e., directly to the `Border` instance. With `componentUseCheck` enabled, the framework checks that every rendered component is used in the markup. Since the body container is hidden but the child is attached to the Border (not the body), the check may fail unless the framework correctly skips the check for components whose hierarchy path leads through an invisible body container.

- **What the test must verify**: The test must call `tester.getApplication().getDebugSettings().setComponentUseCheck(true)`, then `tester.startPage(page)` with the border body hidden, then `tester.assertRenderedPage(...)`. If the fix is missing, this throws a `WicketRuntimeException` about component not being rendered in markup.

- **Common pitfalls to avoid**:
  - Testing only the visible state (hidden=false) — the bug only manifests when hidden=true
  - Adding children to `getBodyContainer()` instead of directly to the `Border` — the bug is about children added to the Border itself when the body is hidden
  - Forgetting to enable `componentUseCheck` — the default may be false in test mode, so explicitly enable it
  - Testing without a full page render — just creating the Border hierarchy is insufficient; the markup rendering must be triggered to see the check failure

### Correct Example
```java
tester.getApplication().getDebugSettings().setComponentUseCheck(true);

HideableBorderPage page = new HideableBorderPage();
page.getBorder().setHidden(true);

tester.startPage(page);
tester.assertRenderedPage(HideableBorderPage.class);
```

### Incorrect Example  
```java
// BUG: Doesn't enable componentUseCheck
HideableBorderPage page = new HideableBorderPage();
page.getBorder().setHidden(true);
tester.startPage(page);

// BUG: Doesn't actually test the hidden state
HideableBorderPage page = new HideableBorderPage();
// setHidden is never called — default is false
tester.startPage(page);
tester.assertRenderedPage(HideableBorderPage.class);
```