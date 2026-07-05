---
name: node-border-div-balance-validation
description: WHEN testing behaviors that write nested HTML opening/closing tags in
  beforeRender/afterRender, THEN verify every opening tag has a matching closing tag
  by asserting the full rendered page output as an expected HTML string. This catches
  unbalanced DIV rendering like the NodeBorder bug where afterRender emitted too many
  closing divs.
code_tags:
- ARRAY_INDEX_ACCESS
- HTML_TAG_BALANCE_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# node-border-div-balance-validation

## Instructions

# NodeBorder Div Balancing Test

## Instructions

- WHEN the TG encounters a `Behavior` subclass (like `NodeBorder`) that writes nested opening HTML tags (e.g. `<div class="...">`) in `beforeRender()` and corresponding closing tags (`</div>`) in `afterRender()`, iterating over an array (`branches[]`).
- THEN the TG should create a test that:
  - Instantiates the behavior with a **non-trivial boolean array** having at least 3 elements with a mix of `true` and `false` values (e.g. `new boolean[] { true, false, true }`).
  - Attaches the behavior to a simple component (e.g. `new Label("label")`).
  - Uses `WicketTester.startComponentInPage(component)` to render the component.
  - Calls `tester.assertResultPage(expectedHtmlString)` with the **full expected HTML string** that includes both the correctly balanced opening and closing tags.
- The test should verify that every `<div>` opened in `beforeRender` has a matching `</div>` in `afterRender`. The expected HTML string should be carefully hand-constructed by tracing the logic of the `beforeRender` loop (which opens divs) and the `afterRender` loop (which closes them).
- **Common pitfall**: Only verifying the presence of certain class names or partial snippets, instead of asserting the full balanced HTML output. The bug manifests as an **unbalanced tree of divs** — the `afterRender` method in the buggy version emits the same number of `</div>` tags regardless of `branches[i]` values, but `beforeRender` emits `<div class="tree-subtree">` only when `i > 0`. This means the opening/closing sequence is mismatched for certain array contents. Only a full-page assertion catches this mismatch.
- **Common pitfall**: Assuming that an even number of tag opens/closes means the HTML is balanced. The issue is the **ordering** of the closing tags relative to the opening tags, so count-based checks (e.g. counting `<div>` vs `</div>`) will NOT catch this bug.

### Example (Correct Test — catches the bug)

```java
WicketTester tester = new WicketTester();

Label label = new Label("label");
label.add(new NodeBorder(new boolean[] { true, false, true }));

tester.startComponentInPage(label);

tester.assertResultPage(
    "<div class=\"tree-branch tree-branch-mid\">" +
    "<div class=\"tree-subtree\">" +
    "<div class=\"tree-branch tree-branch-last\">" +
    "<div class=\"tree-subtree\">" +
    "<div class=\"tree-branch tree-branch-mid\">" +
    "<span wicket:id=\"label\" class=\"tree-node\"></span>" +
    "</div>" +
    "</div>" +
    "</div>" +
    "</div>" +
    "</div>");
```

### Example (Incorrect Test — misses the bug)

```java
// WRONG: Only checks that some divs exist, not the full structure
WicketTester tester = new WicketTester();
Label label = new Label("label");
label.add(new NodeBorder(new boolean[] { true, false, true }));
tester.startComponentInPage(label);
// This passes on buggy code because "tree-branch-mid" does appear
tester.assertContains("tree-branch-mid");
// So does "tree-branch-last"
tester.assertContains("tree-branch-last");
// But the tag structure is unbalanced!
```