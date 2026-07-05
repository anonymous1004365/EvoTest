---
name: visibility-cache-last-tab-annotation
description: WHEN testing components that use a cached visibility state (like VisibilityCache)
  to compute CSS annotations (e.g., "last" class), THEN test that invisible tabs are
  excluded from last-tab calculations even when the selected tab has already been
  resolved in onBeforeRender. This skill prevents stale-cache bugs where the cache
  is computed before visibility is finalized for all tabs.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- CACHING_STALE_STATE
test_pattern: STATE_TEST
---

# visibility-cache-last-tab-annotation

## Instructions

# Visibility Cache Last-Tab Annotation Consistency

## Instructions

- WHEN the TG encounters a component that uses a lazily-initialized, transient inner cache class (e.g., `VisibilityCache`) that computes state (like `getLastVisible()`) and that cache is used during `onComponentTag` (e.g., to add a CSS class like `"last"` to the last *visible* tab)
- THEN the TG should create a test where:
  1. The component has more tabs than are visible (e.g., 2 tabs but only 1 visible).
  2. The first visible tab is also the selected tab (index 0 is visible and selected).
  3. Verify that the *only* visible tab gets the "last" CSS annotation, because there is no later visible tab.
  4. The assertion must check that the rendered HTML contains both the "selected" and "last" classes on the same tab element (e.g., `"tab0 selected last"`).
- Without this skill, the TG might only test cases where all tabs are visible, missing the bug where a cached `getLastVisible()` returns an outdated index (e.g., index 1) while `onConfigure()` later hides the invisible tabs, leaving the wrong tab marked as "last" or none at all.

### Common Pitfalls
- Testing only with all tabs visible — this masks the bug because the last index in the list coincides with the last visible tab.
- Testing only with non-selected, last-visible tab — the bug manifests specifically when the selected tab is also the last visible tab.
- Testing visibility without checking CSS class annotations on the HTML output.
- Forgetting that the `VisibilityCache` is lazily created in `getVisiblityCache()` and its `isVisible(int)` can return a different answer than `onConfigure()` which calls `setVisible()` on each tab container — the cache may not be recomputed between `onBeforeRender` and `onComponentTag`.

### Examples

**Correct Example** (detects the bug):
```java
// Given: a TabbedPanel with 2 tabs, but only 1 visible (e.g., tab0 visible, tab1 invisible)
TabbedPanelVisibilityTestPage page = new TabbedPanelVisibilityTestPage(2, 1);
tester.startPage(page);

// When: the rendered HTML is inspected
List<TagTester> tabsTags = tester.getTagsByWicketId("tabs");

// Then: tab0 (the only visible and selected tab) must have the "last" class
assertEquals("tab0 selected last", tabsTags.get(0).getAttribute("class"));
// Without the fix, this incorrectly produces "tab0 selected" (no "last" class)
```

**Incorrect Example** (misses the bug):
```java
// All tabs visible — does not exercise the stale cache bug
TabbedPanelVisibilityTestPage page = new TabbedPanelVisibilityTestPage(2, 2);
tester.startPage(page);
List<TagTester> tabsTags = tester.getTagsByWicketId("tabs");
assertEquals("tab0 selected", tabsTags.get(0).getAttribute("class"));
assertEquals("tab1 last", tabsTags.get(1).getAttribute("class"));
// This passes on both buggy and fixed versions, giving false sense of correctness.
```