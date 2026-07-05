---
name: border-visibility-impact-on-component-use-check
description: When testing borders that wrap child components, visibility of the border
  container must be tested for its impact on component existence checks. This skill
  detects bugs where a hidden border's child component use check incorrectly considers
  children as "used" despite the border itself being invisible.
code_tags:
- BORDER_VISIBILITY_CHECK
- COMPONENT_USE_CHECK_INTERACTION
test_pattern: INTERACTION_TEST
---

# border-visibility-impact-on-component-use-check

## Instructions

# Border Visibility Impact on Component Use Check

## Instructions

- WHEN the test generator encounters a `Border` subclass that overrides `onComponentTagBody()` or where the border's markup wraps child body components (e.g., `<wicket:border><wicket:body/></wicket:border>`)
- AND when `componentUseCheck` is enabled on `Application.get().getDebugSettings().setComponentUseCheck(true)`
- THEN the test MUST verify that hiding the border (via `setVisible(false)`) does not cause component use check failures for child components added inside the border's `<wicket:body/>` region.
- The test should render a page containing the hidden border, then call `tester.assertNoErrorMessage()` and verify no `WicketRuntimeException` occurs due to "The component(s) below participated in the rendering of the response but are no longer part of the component tree" errors.
- Common pitfalls to avoid: (1) Testing only visible borders — the bug may only manifest when the border is hidden but its children are still added to the component tree; (2) Forgetting to enable `componentUseCheck` in the Application's debug settings before the test; (3) Testing the border in isolation without rendering through a full page with `WicketTester`.

### Correct Example (detects the bug):
```java
@Test
public void componentUseCheck() {
    // Enable component use check
    Application application = Application.get();
    application.getDebugSettings().setComponentUseCheck(true);
    
    // Create and render a page with a hidden border
    HideableBorderPage page = new HideableBorderPage();
    WicketTester tester = new WicketTester(application);
    tester.startPage(page);
    
    // The border's child component should be properly tracked
    // even when the border itself is invisible
    tester.assertNoErrorMessage();
}
```

### Incorrect Example (misses the bug):
```java
// WRONG: Only testing visible borders without enabling componentUseCheck
@Test
public void visibleBorderTest() {
    WicketTester tester = new WicketTester();
    HideableBorderPage page = new HideableBorderPage();
    // Forgetting to set border to visible=false
    // Forgetting to enable componentUseCheck
    tester.startPage(page);
    // This passes even on buggy code because componentUseCheck is off
}
```

### Key Insight:
The bug occurs because when a `Border` is hidden (`isVisible()` returns false), the `Border` class's `onComponentTagBody()` method may still process child components, but the component use check logic confuses the border's invisibility with component abandonment. The fix ensures that hidden borders properly account for their child components' participation in rendering, preventing false positive "component not used" errors.