---
name: markup-cache-variation-testing
description: When marking up variations exist and are cached, the cache may return
  stale markup for different variations if caching keys do not fully account for the
  variation identifier. This skill teaches how to write tests that change a component's
  variation between requests and verify the markup cache returns the correct markup
  for each variation.
code_tags:
- ITERATOR_PATTERN
- STRING_TRANSFORM
- NULL_OR_EMPTY_CHECK
- MARKUP_VARIATION_CACHE
- STATE_MUTATION
test_pattern: STATE_TEST
---

# markup-cache-variation-testing

## Instructions

# Markup Cache Variation Testing

## Instructions

- WHEN testing a component that caches `Markup` objects and supports multiple `variation` values via `getVariation()` or a custom `IMarkupCacheKeyProvider`
- THEN create a test that:
  1. Renders the page/component to populate the markup cache for the initial variation
  2. Changes the variation returned by the component (e.g., by overriding `getVariation()` on the page, or by modifying the component's state)
  3. Renders the page again and verifies the output matches the **new** variation's expected content
  4. The test should assert that specific text patterns unique to each variation appear **only** when the corresponding variation is active

- The test must verify that the cached markup is NOT inadvertently reused across different variations. This means:
  - First render with variation "One" must contain the expected text "One"
  - After changing the variation to "Two" (or another value), the second render must now contain "Two" and NOT "One"
  - If using a `MarkupContainer` or `MarkupCache`, be aware that `remove()` and `add()` operations or other cache-invalidation strategies may be needed

- Common pitfalls:
  - Testing only a single variation without verifying that changing the variation returns different markup
  - Failing to account for markup caching at the application level (e.g., `MarkupCache`) — the test must explicitly issue multiple render calls with different variation states
  - Assuming that modifying state after the first render is sufficient — the test must actually re-render the page/component to trigger a new cache lookup
  - Using `setStatelessHint(false)` or other mechanisms that might force a full page reload rather than testing the cache behavior specifically

### Correct Example
```java
@Test
public void changeVariation()
{
    // First render with variation "One"
    tester.startPage(new VariationPage("One"));
    String doc1 = tester.getLastResponseAsString();
    Assert.assertTrue("Render with variation 'One' must contain 'One'", doc1.contains("One"));

    // Change the page's variation state
    VariationPage page = (VariationPage) tester.getLastRenderedPage();
    page.setVariation("Two");

    // Second render — must use new variation, not cached old one
    tester.startPage(page);
    String doc2 = tester.getLastResponseAsString();
    Assert.assertTrue("Render with variation 'Two' must contain 'Two'", doc2.contains("Two"));
    Assert.assertFalse("Render with variation 'Two' must not contain 'One'", doc2.contains("One"));
}
```

### Incorrect Example
```java
@Test
public void changeVariation()
{
    // Only tests one variation
    tester.startPage(new VariationPage("One"));
    Assert.assertTrue(tester.getLastResponseAsString().contains("One"));
    // Never tests that changing the variation produces different output
}
```