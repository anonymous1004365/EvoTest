---
name: bookmarkable-link-href-with-pageparameters
description: When a BookmarkablePageLink uses PageParameters with a home-page index
  page (e.g., PageParameters with value "0"), the resolved href may produce an unexpected
  URL that fails to render. This skill teaches how to test that the href is correctly
  populated.
code_tags:
- STATE_MUTATION
- EXCEPTION_HANDLING
- VALIDATION
test_pattern: STATE_TEST
---

# bookmarkable-link-href-with-pageparameters

## Instructions

# BookmarkablePageLink Href With PageParameters

## Instructions

- WHEN the TG encounters code that creates a `BookmarkablePageLink` with `PageParameters` (e.g., `new PageParameters().set("param", "value")`) and the link points to a home-page/index page (e.g., `BookmarkableHomePageLinksPage`),
  - THEN it should test that the generated href URL is correctly produced and consistent with expectations.

- WHEN the TG encounters a `BookmarkablePageLink` component inside a page's constructor that is attached via `add()` and uses `PageParameters` with a single integer parameter (e.g., `new PageParameters().set("0", someValue)`),
  - THEN it should verify the rendered href attribute of that link (e.g., by using `Tester.startPage(testPage)` and then `assertContains("href=\"")`) to ensure the link has a non-empty, expected href value.

- Common pitfalls:
  - Testing only that the page is rendered without checking the link's href value — this misses the bug where href is incorrectly formed.
  - Using `PageParameters` with string-typed parameter "0" and expecting integer-based resolution to work the same as string-based resolution.
  - Forgetting to test that the actual href attribute in the rendered markup is correctly set to the expected bookmarkable URL.

- Example (correct test):
```java
@Test
public void testBookmarkableLinkWithPageParameters()
{
    tester.startPage(BookmarkableHomePageLinksPage.class);
    // Verify the page renders without errors
    tester.assertRenderedPage(BookmarkableHomePageLinksPage.class);
    // Verify the link's href is correctly populated
    tester.assertContains("href=\"");
}
```

- Example (incorrect test — too shallow):
```java
@Test
public void testPageRenders()
{
    tester.startPage(BookmarkableHomePageLinksPage.class);
    // Only checks page renders, does NOT verify links have proper href
    tester.assertRenderedPage(BookmarkableHomePageLinksPage.class);
    // Missing: assertContains("href=\"") or similar href validation
}
```