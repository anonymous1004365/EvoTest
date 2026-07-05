---
name: dynamic-panel-header-contribution-stale-state
description: When panels with wicket:head sections are dynamically swapped/replaced
  via AJAX or Link, the old panel's header contribution can become stale/missing and
  the new panel's header may not be re-contributed. Use this skill to write tests
  that verify header contributions are correct after component swaps.
code_tags:
- COMPONENT_REMOVAL_RENDERING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# dynamic-panel-header-contribution-stale-state

## Instructions

# Dynamic Panel Header Contribution Stale State After Swap

## Instructions

- WHEN the TG encounters a test scenario where a Wicket panel component with a `<wicket:head>` section in its markup (e.g., Panel1.html with `<wicket:head>` or `<body onload="...">`) is dynamically swapped/replaced at runtime (e.g., via a `Link` that calls `panel.replaceWith(newPanel)` or `page.addOrReplace(panel)`)
- THEN the TG should write a **state-based test** that:
  1. Renders the page to get the initial output (including headers from the first panel)
  2. Clicks the link / triggers the component swap action using `tester.clickLink(...)` or similar
  3. Renders the page again after the swap
  4. Verifies that the rendered output contains the new panel's header contribution (e.g., `Panel 1` body content and its `<wicket:head>` / `<body onload>` attributes)
  5. Verifies that the old panel's header contribution is no longer present in the output
  6. Compares the rendered output against expected result files (e.g., `TestPage_ExpectedResult-1.html` for initial state, `TestPage_ExpectedResult-2.html` for post-swap state)
- Include **concrete** values: use `tester.assertContains("...")` or `tester.assertResultPage(Class)` with the actual expected result file names
- Common pitfalls to avoid:
  - Testing only the initial render without the swap/replacement step
  - Forgetting that `<wicket:head>` content (JavaScript, CSS, `<body onload>`) needs to be re-contributed when the contributing component is swapped
  - Only checking the panel body content but not the `<head>` section (the header contribution may be missing even though the body renders correctly)
  - Using `tester.assertContains(...)` on partial strings that could match both states (be specific enough to distinguish old vs new panel content)

### Correct Example (Java)
```java
// Test that panel headers are correctly contributed after dynamic swap
@Test
public void testPanelHeaderAfterSwap() {
    // Render initial page with Panel1
    tester.executeTest(TestPage.class);
    tester.assertResultPage(TestPage.class, TestPage_ExpectedResult_1.class);
    
    // Click link to swap Panel1 -> Panel2
    tester.clickLink("link");
    
    // After swap, verify Panel2's header and body are present
    tester.assertResultPage(TestPage.class, TestPage_ExpectedResult_2.class);
    
    // Also verify body content of the swapped panel
    String doc = tester.getLastResponse().getDocument();
    assertTrue("Panel 2 body content should be present", doc.contains("Panel 2"));
}
```

### Incorrect Example (Missing Swap Verification)
```java
// BAD: Only tests initial render, does not test state after swap
@Test
public void testInitialPanelHeader() {
    tester.executeTest(TestPage.class);
    tester.assertResultPage(TestPage.class, TestPage_ExpectedResult_1.class);
    // Missing: no clickLink, no post-swap assertion
}
```