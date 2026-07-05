---
name: ajax-inlineenclosure-placeholder-rendering
description: When testing InlineEnclosure components toggled via Ajax, verify that
  the placeholder markup (style="display:none") appears in the Ajax response when
  the enclosure is hidden, not just when the page is first rendered. This skill catches
  missing placeholder rendering in Ajax responses.
code_tags:
- COMPONENT_ADDITION_ID
- CHILD_ADDITION_REPLACE
- AJAX_INLINECLOSURE_PLACEHOLDER
test_pattern: INTERACTION_TEST
---

# ajax-inlineenclosure-placeholder-rendering

## Instructions

# Ajax InlineEnclosure Placeholder Rendering in Ajax Responses

## Instructions

- WHEN the TG encounters an `InlineEnclosure` component (from `org.apache.wicket.markup.html.internal.InlineEnclosure`) that wraps other components and is toggled via an Ajax link (e.g., `AjaxLink` or `AjaxFallbackLink`),
- THEN the TG should:
  1. Create a test page that uses `wicket:enclosure="componentId"` attribute in the HTML markup on a `<tr>`, `<div>`, or other container element
  2. Include an `AjaxLink` or similar Ajax component in the page that toggles the visibility of the enclosed component by calling `setVisible(!component.isVisible())` on the enclosed component (not the enclosure itself)
  3. After an Ajax request that makes the enclosed component invisible, verify that the Ajax response contains the placeholder markup for the InlineEnclosure, specifically a pattern like `<tr id="wicket_InlineEnclosure-0" style="display:none">` (inside the Ajax response body)
  4. Use `WicketTester` methods such as:
     - `tester.startPage(page)`
     - `tester.clickLink(linkComponent, true)` (with `true` to follow Ajax)
     - `tester.assertComponentOnAjaxResponse(componentClass)` to check what's in the Ajax response
     - `tester.getLastResponseAsString()` and use string matching (e.g., `assertTrue(response.contains(expectedPattern))`) to verify placeholder presence
  5. Test both visibility states:
     - When the enclosed component IS visible, the InlineEnclosure markup should render normally (showing the content)
     - When the enclosed component is NOT visible, the InlineEnclosure should render as a placeholder with `style="display:none"` in the Ajax response

- Common pitfalls to avoid:
  - ❌ Testing only on initial page render (first request) and not checking the Ajax response after toggling visibility
  - ❌ Using `tester.clickLink(component)` without the `true` argument for Ajax, which won't properly process the Ajax request
  - ❌ Testing the InlineEnclosure placeholder only with `setOutputMarkupId(true)` on a single component, when InlineEnclosure uses `setOutputMarkupPlaceholderTag(true)` internally and needs the Ajax response to include the full placeholder tag
  - ❌ Verifying the component's visibility state programmatically (e.g., `assertFalse(component.isVisible())`) without also checking that the rendered Ajax response actually contains the placeholder HTML
  - ❌ Assuming that because the placeholder appears on initial page load, it will also appear in Ajax responses

- Example correct test pattern:
```java
// Given a page with an InlineEnclosure and an AjaxLink that toggles a component inside it
Page page = new MyInlineEnclosureAjaxPage();
tester.startPage(page);
// When the user clicks the toggle link to HIDE the enclosed component
tester.clickLink("link", true); // true = process Ajax
// Then the Ajax response should contain the placeholder for the InlineEnclosure
String response = tester.getLastResponseAsString();
assertTrue("Expected placeholder in Ajax response when enclosure is hidden",
    response.contains("style=\"display:none\""));
// Or more specifically:
assertTrue("Expected InlineEnclosure placeholder in Ajax response",
    response.contains("<tr id=\"wicket_InlineEnclosure-0\" style=\"display:none\">"));
```

- Example incorrect test pattern (what to avoid):
```java
// ❌ BAD: Only tests initial render, not Ajax response
Page page = new MyInlineEnclosureAjaxPage();
tester.startPage(page);
// After toggle, checks component state but not rendered output
tester.clickLink("link"); // missing true for Ajax
assertFalse(component.isVisible());
// ❌ Missing: checking the Ajax response HTML for the placeholder tag
```