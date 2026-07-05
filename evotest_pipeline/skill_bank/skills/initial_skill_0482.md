---
name: paged-list-navigation-integration
description: When testing pageable list views with pagination navigation, verify that
  navigation links render correctly after state changes like page clicks. The TG should
  test that after navigating to a different page, both the list items and the navigation
  bar update correctly.
code_tags:
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# paged-list-navigation-integration

## Instructions

# Pageable List Navigation Integration Testing

## Instructions

- WHEN the TG encounters a `PageableListView` or any `IPageable` component combined with a `PagingNavigation`
- THEN it should write a test that:
  1. Renders the page with the initial state
  2. Clicks on a navigation link (e.g., a `PagingNavigationLink`) to change the current page
  3. Verifies that the rendered output changes correctly — both the list items displayed AND the navigation bar links update properly
  4. Verifies that navigation links still point to valid page numbers after the page change (e.g., clicking page 2 should still show page 1 and page 2 as valid navigation options, and the correct items for page 2 should be shown)

- WHEN testing navigation clicks on pageable list views (e.g., `PageableListView`)
- THEN the test should verify:
  - The page count (`pageable.getPageCount()`) is correct given the item count and items-per-page
  - After clicking a navigation link, the rendered page shows items from the correct page (using offset calculations like `getCurrentPage() * getItemsPerPage()`)
  - After navigation, the `PagingNavigation` still renders links covering the correct page range

- Common pitfalls to avoid:
  - Testing only the initial page render without clicking navigation links
  - Testing page count without verifying navigation links update after state changes
  - Not verifying that navigation links continue to point to valid pages (no IndexOutOfBounds or stale links)
  - Clicking navigation links without checking that the navigation bar itself re-renders correctly
  - Using low item counts that don't produce enough pages to test navigation properly — use enough items to create at least 2 pages

**Correct example** (3 items, 2 per page = 2 pages):
```java
tester.startPage(PagedTablePage.class);
String document = tester.getLastResponseAsString();
// Verify page 1 shows items "one" and "two" (not "three")
assertTrue(validatePage1(document));

// Click the navigation link for page 2
Link<?> link = (Link<?>)page.get("navigation:1:pageLink");
tester.clickLink(link.getPageRelativePath());
document = tester.getLastResponseAsString();
// Verify page 2 shows item "three" and navigation still shows both page links
DiffUtil.validatePage(document, this.getClass(), "PagedTablePageExpectedResult.html", true);
```

**Incorrect example** (only tests initial page, no navigation):
```java
tester.startPage(PagedTablePage.class);
// Only verifies the initial page — misses the bug entirely
assertTrue(validatePage1(document));
// No click on navigation link, no verification of navigation after page change
```