---
name: enclosure-placeholder-rendering
description: When testing Enclosure component rendering with placeholder tags, the
  TG should verify that wicket:id placeholder markup in enclosed body sections is
  correctly substituted with component output. The `testRender10` test exposed a rendering
  issue where placeholder interpolation failed during Enclosure rendering, causing
  fixture mismatch.
code_tags:
- RENDER_OUTPUT_COMPARISON
- MARKUP_INTERPOLATION
test_pattern: PARAMETRIC_TEST
---

# enclosure-placeholder-rendering

## Instructions

# Enclosure Placeholder Rendering Verification

## Instructions

- WHEN the TG encounters a test case for `Enclosure` component rendering (any class that extends or uses `org.apache.wicket.markup.html.internal.Enclosure`)
- THEN the TG should write a test that:
  1. Creates a page containing an `Enclosure` component that wraps child markup including `wicket:id` placeholder tags (e.g., `<span wicket:id="label">` inside the enclosure body)
  2. Starts the page with `WicketTester` and calls `tester.startPage(page)`
  3. Compares the full rendered output against an expected HTML fixture file (e.g., `EnclosurePageExpectedResult_XX.html`) by calling `tester.assertResultPage(ExpectedResultClass.class)` or equivalent `MarkupComparator` comparison
  4. Verifies that ALL `wicket:id` placeholders within the enclosure body are properly interpolated/replaced with actual component output (not left as raw wicket:id attributes in the output)
- Common pitfalls to avoid:
  - Testing only that the enclosure renders without error, without checking the actual HTML output against a known-good fixture
  - Assuming that enclosure body content is rendered identically to non-enclosure content — the Enclosure component has special markup processing that can affect placeholder interpolation
  - Using only programmatic assertions on component models without verifying the full markup output, which would miss rendering bugs at the markup processing level
  - Forgetting that Enclosure uses `WicketTagIdentifier` and custom tag interpolation that differs from regular component rendering — any change to how wicket:id placeholders are resolved inside enclosed regions can break output

### Correct Example (mimicking testRender10 pattern)
```java
@Test
public void enclosureRendersPlaceholdersCorrectly() throws Exception
{
    // Create a page where an Enclosure component wraps children with wicket:id placeholders
    Class<? extends Page> clazz = EnclosurePage_WithPlaceholders.class;
    tester.startPage(clazz);
    tester.assertResultPage(EnclosurePageExpectedResult_WithPlaceholders.class);
}
```

### Incorrect Example
```java
@Test
public void testEnclosure()
{
    // WRONG: Only checks the component renders, not the full markup output
    Enclosure enclosure = new Enclosure("enclosure", ...);
    assertNotNull(enclosure);
    assertTrue(enclosure.isVisible());
    // Does NOT check if wicket:id placeholder interpolation inside the enclosure is correct
}
```