---
name: dequeueing-transparent-container-markup-resolution
description: When a TransparentWebMarkupContainer participates in queueing/child markup
  resolution, test that the markup of child pages is correctly rendered. This skill
  catches bugs where the dequeueing mechanism fails under transparent container hierarchies.
code_tags:
- QUEUEING
- COMPONENT_RESOLUTION
test_pattern: STATE_TEST
---

# dequeueing-transparent-container-markup-resolution

## Instructions

# Dequeueing Transparent Container Markup Resolution

## Instructions

- WHEN the TG encounters a test scenario involving a `TransparentWebMarkupContainer` that wraps a `<wicket:child/>` region in a parent page (e.g., `BasePage`), where a child page (e.g., `SubPage`) extends the parent via `<wicket:extend>` and contains additional wicket components
- THEN the TG should write a test that:
  1. Creates a `WebPage` (e.g., `TransparentContainerQueuePage`) that uses a `TransparentWebMarkupContainer` (e.g., named `"html"`) at the `<html>` tag level
  2. This page contains markup that includes a `<wicket:child/>` region where child page content will be rendered
  3. Creates a separate child page class (e.g., `SubPage`) extending the parent, which overrides the `<wicket:extend>` block
  4. Uses `wicketTester.startPage(childPageClass)` where `childPageClass` is the subclass (not the parent), so the rendering goes through the queueing/dequeueing code path
  5. Calls `wicketTester.assertContains("Sub page")` (or an assertion on the expected rendered text) to verify the child page content is actually rendered
  6. Tests that a `TransparentWebMarkupContainer` with a `wicket:id` matching the `<html>` tag's `wicket:id` does NOT absorb/consume child markup during dequeueing

- Common pitfalls to avoid:
  - Only testing `startPage(parentPage)` instead of `startPage(childPage)` — the bug only manifests when a child page participates in the dequeueing
  - Not including a `TransparentWebMarkupContainer` in the page that wraps the `<wicket:child/>` region — the transparency is critical
  - Forgetting that the markup must include self-closing or non-closing tags (like `<img>`) that can interfere with the transparent container's dequeueing logic
  - Testing only the setup without verifying the output contains expected child page content

### Example (correct approach):

```java
// In TransparentContainerQueuePage.html:
// <html wicket:id="html" xmlns:wicket="http://wicket.apache.org">
//   <body>
//     <div id="ft"><wicket:child/></div>
//   </body>
// </html>

// In BasePage.html:
// ...<wicket:child/>...

// In SubPage.html:
// <wicket:extend>
//   <img alt="foo" src="bar">
//   Sub page
//   <span wicket:id="version">1.5-SNAPSHOT</span>
// </wicket:extend>

// Test:
@Test
public void startSubPageWithTWMCinTheParentPage() {
    TransparentContainerQueuePage page = new TransparentContainerQueuePage();
    SubPage subPage = new SubPage(page);
    wicketTester.startPage(subPage);
    // Bug: without fix, this throws MarkupException because transparent container
    // incorrectly consumes/resolves the child markup during dequeueing
    wicketTester.assertContains("Sub page");
}
```

### Example (incorrect approach):

```java
// WRONG: Only testing the parent page without a child subclass
@Test
public void startParentPageOnly() {
    // This does not trigger the dequeueing code path with transparent containers
    wicketTester.startPage(new TransparentContainerQueuePage());
    // The test passes even on the buggy version, giving false confidence
}

// WRONG: Not using a TransparentWebMarkupContainer
@Test
public void startChildPageWithoutTransparentContainer() {
    // Without the transparent container wrapping <wicket:child/>, 
    // the bug's triggering condition is not met
    wicketTester.startPage(new SubPage(somePage));
    wicketTester.assertContains("Sub page");
}
```