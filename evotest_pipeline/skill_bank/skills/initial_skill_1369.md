---
name: wicket-header-items-duplicate-validation
description: WHEN validating that only one <wicket:header-items/> tag exists in a
  page's <head> element THEN the test should verify that a page with an inherited
  header from a base page that already has <wicket:header-items/> does NOT throw a
  "More than one" exception. Use this skill when testing header items container behavior
  in Apache Wicket.
code_tags:
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# wicket-header-items-duplicate-validation

## Instructions

# Wicket Header Items Duplicate Validation

## Instructions

- WHEN the TG encounters code that validates `<wicket:header-items/>` tags in the `<head>` element using `HtmlHeaderItemsContainer`, `HtmlHeaderContainer`, or `HtmlHeaderSectionHandler`
- THEN the TG should write a test that creates a base page containing a `<wicket:header-items/>` tag in its `<head>`, and a child page that extends that base page and also has its own `<head>` element — BUT without a second `<wicket:header-items/>` in the child page.
- The test must verify that NO `WicketRuntimeException` with message containing "More than one <wicket:header-items/>" is thrown when rendering the child page
- AND the test should also verify that when a page has two `<wicket:header-items/>` tags in the same `<head>` (duplicate), the correct exception IS thrown with the message "More than one <wicket:header-items/> detected in the <head> element. Only one is allowed."
- COMMON PITFALL: Testing only the positive case (expecting an exception on duplicates) without testing the negative case (no exception when the parent provides the header-items). The bug is that the validation falsely detects a duplicate when a base page already has `<wicket:header-items/>` and the extending page simply has its own `<head>` tag.
- The TG MUST use `org.apache.wicket.util.tester.WicketTester` (or `WicketTestCase`) to render pages and catch/assert on the exception behavior.
- EXPECTED EXCEPTION CLASS: `org.apache.wicket.WicketRuntimeException` with message "More than one <wicket:header-items/> detected in the <head> element. Only one is allowed." — this should be thrown for the truly duplicate case, but NOT thrown when the parent provides the single header-items.

### Correct example (positive case — expects exception):
```java
// Page with two <wicket:header-items/> in its own markup — should throw
@Test
void pageWithDuplicateHeaderItemsThrowsException() {
    assertThrows(WicketRuntimeException.class, () -> {
        tester.startPage(PageWithTwoHeaderItems.class);
    });
}
```

### Correct example (negative case — tests the bug fix):
```java
// Child page that extends a base page with <wicket:header-items/>
// The child should NOT throw because the parent provides the single header-items
@Test
void pageExtendingBasePageWithHeaderItemsDoesNotThrow() {
    Assertions.assertDoesNotThrow(() -> {
        tester.startPage(MyBasePageUsingChildPage.class);
    });
}
```

### Incorrect example (would miss the bug):
```java
// Only testing the duplicate case — misses the regression entirely
@Test
void testDuplicateHeaderItems() {
    try {
        tester.startPage(PageWithTwoHeaderItems.class);
        fail("Expected exception");
    } catch (Exception e) {
        // OK
    }
}
```