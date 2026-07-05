---
name: inline-enclosure-wicket-message-rendering
description: WHEN an InlineEnclosure component has a child component with a wicket:message
  attribute (e.g. wicket:message="title:titleAttr"), THEN test both visible and invisible
  states to ensure the markup renders correctly and the expected output matches exactly.
  This skill catches bugs where InlineEnclosure handlers incorrectly process or omit
  wicket:message attributes during enclosure boundary resolution.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- AJAX_INLINECLOSURE_PLACEHOLDER
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# inline-enclosure-wicket-message-rendering

## Instructions

# InlineEnclosure with wicket:message Rendering

## Instructions

WHEN the TG encounters a test class that tests `InlineEnclosure` components with `wicket:message` attributes on the same tag, THEN the TG should:

1. **Test both visible and invisible states**: Create two test methods or a parametrized test — one where the enclosure child is visible (e.g., `child.setVisible(true)`) and one where it is invisible (`child.setVisible(false)`).
2. **Use exact expected HTML files**: Compare the rendered output against expected HTML fixture files (e.g., `InlineEnclosureWithWicketMessagePage_visible_expected.html` and `InlineEnclosureWithWicketMessagePage_invisible_expected.html`).
3. **Verify wicket:message attribute appears in the output**: The expected HTML should contain the resolved wicket:message attribute (e.g., `title="someValue"`) when the component is visible and omit the child markup when invisible.
4. **Use the test framework's standard rendering and assertion pattern**: For Wicket, use `tester.startPage(InlineEnclosureWithWicketMessagePage.class)` followed by `tester.assertResultPage(InlineEnclosureWithWicketMessagePage.class, "InlineEnclosureWithWicketMessagePage_visible_expected.html")`.

Common pitfalls:
- Testing only one visibility state (e.g., only visible) and missing the boundary case of invisible components with wicket:message.
- Using `tester.assertContains(...)` or partial string matching instead of `tester.assertResultPage(...)` which does exact markup comparison.
- Forgetting to set up the test page class and expected HTML files with the proper resource naming convention (test class name + `_{state}_expected.html`).
- Not adding `@Test` annotation to both test methods.

### Correct Example

```java
@Test
public void inlineEnclosureWithWicketMessageVisible() throws Exception
{
    InlineEnclosureWithWicketMessagePage page = new InlineEnclosureWithWicketMessagePage();
    page.get("child").setVisible(true);
    tester.startPage(page);
    tester.assertResultPage(InlineEnclosureWithWicketMessagePage.class,
            "InlineEnclosureWithWicketMessagePage_visible_expected.html");
}

@Test
public void inlineEnclosureWithWicketMessageInvisible() throws Exception
{
    InlineEnclosureWithWicketMessagePage page = new InlineEnclosureWithWicketMessagePage();
    page.get("child").setVisible(false);
    tester.startPage(page);
    tester.assertResultPage(InlineEnclosureWithWicketMessagePage.class,
            "InlineEnclosureWithWicketMessagePage_invisible_expected.html");
}
```

### Incorrect Example

```java
// BAD: Only tests visible state, misses invisible case
@Test
public void inlineEnclosureWithWicketMessage() throws Exception
{
    tester.startPage(InlineEnclosureWithWicketMessagePage.class);
    tester.assertContains("title=\"someValue\""); // partial match, not exact
}
```