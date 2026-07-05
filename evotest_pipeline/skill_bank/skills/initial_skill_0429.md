---
name: partial-page-update-header-contributions
description: When testing page re-rendering and partial updates, verify that header
  contributions (CSS/JS) are properly included in each rendering, not just on initial
  render. This skill detects bugs where header items are incorrectly cached/stripped
  after the first render of a page.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- COLLECTION_OPERATIONS
test_pattern: STATE_TEST
---

# partial-page-update-header-contributions

## Instructions

# Partial Page Update Header Contributions

## Instructions

WHEN the TG encounters code that:
- Uses `PartialPageUpdate` (or subclasses like `XmlPartialPageUpdate`) to generate Ajax responses that include page header contributions (CSS, JavaScript)
- Re-renders a page after its initial render (e.g., a second Ajax request triggers the same page's rendering)
- Has header contribution logic that collects items into a data structure (e.g., `List`, `Set`, `Map`) during rendering

THEN the TG should:
1. Verify that header contribution items (e.g., `<link>` stylesheet references, `<script>` tags) appear in EVERY partial page update response, not just the first one
2. Create a test that:
   a. Renders the page once (initial Ajax request) — verify header contributions appear
   b. Triggers a second re-render of the same page (e.g., via `tester.executeAjaxEvent` or URL re-request) — verify header contributions STILL appear in the second response
3. Assert that the expected header content (e.g., a specific `<link>` tag for a CSS file or a `<script>` tag) is present in the response body for BOTH renderings
4. If the test fails with a "pattern not found" assertion error, that signals the bug: the second rendering lost the header contributions

Common pitfalls to avoid:
- Testing only a SINGLE render request — the bug only manifests on RE-rendering (second or subsequent requests)
- Only testing component body content without checking for header contributions (CSS `<link>`, JS `<script>`)
- Using `assertInPage` or similar which may only check the last response — instead capture and inspect BOTH response bodies explicitly
- Assuming that once header items are rendered, they persist across re-renders

Expected exception/failure on buggy version:
- The second response body will be MISSING expected HTML header elements (`<link>`, `<script>`, or `<style>` tags)
- Test assertion (e.g., `assertContains("...")`) will fail with "pattern not found" for the second response

### Correct Example (catches the bug)
```java
// Test that header contributions survive a page re-render
tester.startPage(page);
tester.assertContains("myTheme.css"); // first render: OK

// Trigger a re-render of the same page
tester.executeAjaxEvent("component", "event");
tester.assertContains("myTheme.css"); // second render: FAILS on buggy version
```

### Incorrect Example (misses the bug)
```java
// Only testing initial render — passes even with the bug
tester.startPage(page);
tester.assertContains("myTheme.css");

// Never re-renders the page to check header contributions survive
```