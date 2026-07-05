---
name: data-table-conditional-element-rendering
description: WHEN a DataTable renders conditional HTML elements (thead/tfoot/caption)
  that depend on toolbar visibility or model state, THEN test that the HTML output
  correctly includes or excludes those elements under different conditions. This skill
  helps catch bugs where conditional rendering logic in component HTML markup doesn't
  match the expected W3C HTML structure.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- CONDITIONAL_RENDERING
test_pattern: STATE_TEST
---

# data-table-conditional-element-rendering

## Instructions

# DataTable Conditional Element Rendering

## Instructions

- WHEN the TG encounters a `DataTable` (or similar panel-based component) that renders conditional HTML structural elements (like `<thead>`, `<tfoot>`, `<caption>`, `<colgroup>`) based on the visibility/state of child components (e.g., toolbars container, caption model)
- THEN the TG should write a state-based test that:
  1. Renders the DataTable under different conditions (e.g., with items vs. without items, with visible toolbars vs. invisible toolbars, with caption model set vs. null)
  2. Asserts that the rendered HTML contains the correct structural elements when expected AND does NOT contain them when not expected
  3. Specifically:
     - Verify `<thead>` is rendered ONLY when `topToolbars` have visible children, and `<tfoot>` ONLY when `bottomToolbars` have visible children
     - Verify `<caption>` is rendered ONLY when `getCaptionModel()` returns a non-null model AND the model value is non-empty
     - Verify that there is exactly one `<thead>` and one `<tfoot>` when they are present (per HTML spec)

- WHEN the TG tests conditional rendering via `getLastResponseAsString()` string inspection
- THEN the TG should use `assertTrue(document.contains("..."))` and `assertFalse(document.contains("..."))` for HTML structural elements, not just component visibility checks

- DO NOT test only the Java-side component visibility — the bug may be that components are present in the component tree but the HTML markup produces incorrect structure (e.g., missing `<thead>` when `topToolbars` has invisible children, or producing `<thead>` when all children are invisible)
- DO NOT assume that adding a toolbar with invisible components will suppress the `<thead>`/`<tfoot>` — the bug may be that the `ToolbarsContainer` still renders the enclosing `<thead>`/`<tfoot>` even when all its toolbar children are invisible

### Correct example pattern

```java
// Test that thead/tfoot are suppressed when toolbars have only invisible children
PageParameters params = new PageParameters();
params.add("empty", Boolean.TRUE);
tester.startPage(Wicket3603Page.class, params);
String response = tester.getLastResponseAsString();
assertFalse("Expected no <thead> when topToolbars have no visible children", 
    response.contains("<thead"));
assertFalse("Expected no <tfoot> when bottomToolbars have no visible children", 
    response.contains("<tfoot"));

// Test that thead/tfoot are present when toolbars have visible children  
params.set("empty", Boolean.FALSE);
tester.startPage(Wicket3603Page.class, params);
response = tester.getLastResponseAsString();
assertTrue("Expected <thead> when topToolbars have visible children", 
    response.contains("<thead"));
assertTrue("Expected <tfoot> when bottomToolbars have visible children", 
    response.contains("<tfoot"));
```

### Incorrect example pattern

```java
// WRONG: Only checks component tree visibility, not HTML output
DataTable<?, ?> table = new DataTable<>("table", columns, provider, 10);
table.addBottomToolbar(new NoRecordsToolbar(table));
assertTrue("Toolbar is visible", table.getBottomToolbars().isVisible());
// This misses the bug where the <tfoot> tag is rendered even when
// the NoRecordsToolbar is invisible (because there ARE records)
```