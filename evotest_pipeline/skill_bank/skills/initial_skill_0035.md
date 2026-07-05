---
name: border-body-visibility-component-use-check
description: When testing a Wicket Border whose body starts hidden, the TG should
  verify that DebugSettings.setComponentUseCheck(true) does not throw a component-use-check
  failure. This catches cases where children added to the Border instead of its body
  cause false positives in the component use check.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CHILD_REMOVAL
test_pattern: STATE_TEST
---

# border-body-visibility-component-use-check

## Instructions

# Border Body Visibility Component Use Check

## Instructions

- WHEN the TG sees a `Border` subclass that has a `setHidden(boolean)` method or a similar mechanism to hide its body container (e.g., a `WebMarkupContainer` wrapper around the body whose `isVisible()` depends on a `hidden` boolean flag)
- THEN the TG MUST write a state-based test that does the following:
  1. Enables component use checking by calling `tester.getApplication().getDebugSettings().setComponentUseCheck(true)` before starting the page
  2. Instantiates the page containing the Border
  3. Sets the border hidden BEFORE the page is rendered (e.g., `page.getBorder().setHidden(true)`)
  4. Starts the page with `tester.startPage(page)`
  5. Verifies the page renders correctly with `tester.assertRenderedPage(PageClass.class)`
  6. The test MUST NOT expect any exception — the component use check should not fire

- Common pitfalls to avoid:
  - Do NOT test only with the border visible — the bug only manifests when the border body starts hidden and component use checking is enabled
  - Do NOT forget to enable `componentUseCheck` before starting the page, as it is disabled by default
  - Do NOT use `getBodyContainer().add(child)` to add children to the Border — the `border.add(child)` method routes child components to `getBodyContainer()` automatically, but if a child is added directly to the border's body container and the body is hidden, the component use check may incorrectly flag the child as unrendered
  - Do NOT test the `hideableBorder` scenario (AJAX toggling) as a replacement — the component use check failure occurs specifically when the border starts hidden, not when toggling visibility later

### Correct Example

```java
@Test
public void componentUseCheck() throws Exception
{
    tester.getApplication().getDebugSettings().setComponentUseCheck(true);

    HideableBorderPage page = new HideableBorderPage();
    // start with border body hidden
    page.getBorder().setHidden(true);

    tester.startPage(page);
    tester.assertRenderedPage(HideableBorderPage.class);
}
```

### Incorrect Example (missing componentUseCheck enabling)

```java
@Test
public void componentUseCheck() throws Exception
{
    // BUG: componentUseCheck not enabled!
    HideableBorderPage page = new HideableBorderPage();
    page.getBorder().setHidden(true);
    tester.startPage(page);
    tester.assertRenderedPage(HideableBorderPage.class);
    // This test passes even with the bug present
}
```

### Incorrect Example (testing only visible state)

```java
@Test
public void componentUseCheck() throws Exception
{
    tester.getApplication().getDebugSettings().setComponentUseCheck(true);

    HideableBorderPage page = new HideableBorderPage();
    // BUG: border is visible by default, doesn't exercise the buggy path
    // page.getBorder().setHidden(true) is missing!

    tester.startPage(page);
    tester.assertRenderedPage(HideableBorderPage.class);
}
```