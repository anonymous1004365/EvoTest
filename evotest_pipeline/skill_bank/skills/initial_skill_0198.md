---
name: enclosure-render-visibility-child-removal
description: When testing Wicket Enclosure components, verify that when an Enclosure
  is invisible, its child components are still properly rendered without being removed
  or causing errors. This skill applies to tests that render a page containing Enclosure
  components with invisible state.
code_tags:
- ENCLOSURE_INTERACTION
- COMPONENT_TREE_NAVIGATION
- CHILD_REMOVAL
- ENCLOSURE_VISIBILITY_RENDER
test_pattern: PARAMETRIC_TEST
---

# enclosure-render-visibility-child-removal

## Instructions

# Enclosure Render Visibility and Child Component Removal

## Instructions

- WHEN the TG encounters a test that renders a Wicket `Enclosure` component containing child components (e.g., `Label`, `Link`, or other Wicket components), AND the Enclosure's visibility is set to `false` via a model expression (e.g., `wicket:enclosure` visibility depends on a panel/child not being `null`)
- THEN the TG should create a test page (extending `WebPage`) that:
  1. Contains an `Enclosure` whose visibility evaluates to `false` (e.g., a condition where a referenced component is `null` or `false`)
  2. Has child components inside the Enclosure markup
  3. Renders the page using `WicketTester` and calls `tester.startPage(TestPageClass.class)`
  4. Verifies that no exceptions (e.g., `NullPointerException`, `IllegalStateException`) are thrown during render
  5. Verifies the rendered response is not empty and the invisible content is properly excluded from output
- WHEN testing Enclosure behavior with invisible child conditions, the TG MUST ensure the test exercises the render path where the Enclosure is invisible but still processes its children during the render phase — this is where removal or null-pointer bugs occur
- Common pitfalls to avoid:
  - Testing only with visible Enclosures (the default happy path), missing the invisible case
  - Assuming that invisible Enclosures skip child rendering entirely — in Wicket, children may still be visited during render traversal, and if they are removed or not properly guarded, a `NullPointerException` can occur
  - Using only unit tests on the Enclosure component in isolation — prefer integration tests using `WicketTester` that render the full page markup
  - Not providing an HTML markup file for the test page (e.g., `EnclosurePage_7.html`) — the Wicket tester requires matching markup
  - Testing with trivial child components (e.g., empty labels) — use components with real behavior to exercise the render path

### Correct Example (catches the bug)

```java
// Test page (EnclosurePage_7.java)
public class EnclosurePage_7 extends WebPage {
    public EnclosurePage_7() {
        // A panel that is null - makes the Enclosure invisible
        add(new Label("label", "test"));
    }
}

// HTML markup (EnclosurePage_7.html) — the Enclosure wraps around components
// but since its model condition is false, it should be invisible
<html><body>
  <div wicket:enclosure="panel">
    <span wicket:id="label">text</span>
  </div>
</body></html>

// Test method
@Test
public void testRender() {
    WicketTester tester = new WicketTester(application);
    tester.startPage(EnclosurePage_7.class);
    // No exception should be thrown during render
    assertNotNull(tester.getLastResponse().getDocument());
}
```

### Incorrect Example (misses the bug)

```java
// Only tests visible Enclosure — doesn't exercise the buggy path
@Test
public void testVisibleEnclosure() {
    WicketTester tester = new WicketTester(application);
    tester.startPage(EnclosurePage_Visible.class); // Enclosure is always visible
    // The bug only triggers when Enclosure is invisible, so this test passes even on buggy code
}
```