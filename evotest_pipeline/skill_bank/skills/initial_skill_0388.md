---
name: transparent-resolver-markup-for-ajax-panels
description: WHEN a panel is nested inside a TransparentWebMarkupContainer and rendered
  via AJAX, the PanelMarkupSourcingStrategy may fail to resolve the panel's markup.
  THEN the test must render the page using an AJAX request (or render the page with
  a state that triggers AJAX rendering) and verify that nested panels correctly resolve
  their associated markup.
code_tags:
- COMPONENT_TREE_NAVIGATION
- MARKUP_RESOLUTION
test_pattern: STATE_TEST
---

# transparent-resolver-markup-for-ajax-panels

## Instructions

# Transparent Resolver Markup for AJAX Panels

## Instructions

- WHEN the TG encounters a `TransparentWebMarkupContainer` that wraps a Panel component (e.g., `BasePanel` with a child panel like `InnerPanel` via `wicket:id`), and the page state is changed via an AJAX link/button that re-renders the container
- THEN the test should:
  1. Create a page that uses a `TransparentWebMarkupContainer` with `wicket:id="transparent"` containing a nested panel (e.g., `<div wicket:id="innerpanel"></div>`)
  2. Include an AJAX link/button inside the transparent container that updates the page state (e.g., clicking a link changes a model value)
  3. Render the page initially to verify no `MarkupNotFoundException` occurs
  4. Simulate an AJAX request by clicking the AJAX link (using `tester.clickLink(...)`) and verify the second render also succeeds without `MarkupNotFoundException`
- Verify that the markup for inner panels is correctly resolved **both** on initial render AND on AJAX re-render. The bug is that on the second render (AJAX), `PanelMarkupSourcingStrategy` fails to find the markup because it doesn't properly search through the transparent resolver's markup.
- Common pitfalls:
  - Testing only the initial (non-AJAX) render — the bug only manifests on AJAX re-render
  - Testing only simple panel nesting without `TransparentWebMarkupContainer` wrapping
  - Not including an inner component that triggers the `PanelMarkupSourcingStrategy` markup resolution path
- Correct example (expected behavior — the fixed version passes):
```java
// Bug: Markup not found for component [innerpanel] on AJAX re-render
// Page: HomePage with <div wicket:id="panel"> BasePanel containing TransparentWebMarkupContainer 
//       with child panel (wicket:id="innerpanel") and AJAX link (wicket:id="link")
tester.startPage(HomePage.class);
tester.assertNoErrorMessage();  // initial render succeeds

tester.clickLink("panel:link"); // AJAX re-render
tester.assertNoErrorMessage();  // fails on buggy version: "Markup not found for Component: [Component id = innerpanel]"
```

- Incorrect example (would not catch the bug):
```java
tester.startPage(HomePage.class);
tester.assertNoErrorMessage();  // passes on both buggy and fixed — not enough
// Missing the AJAX re-render step!
```

- The failure message on the buggy version is: `"Markup not found for Component: [Component id = innerpanel]"`