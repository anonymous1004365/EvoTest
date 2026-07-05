---
name: merged-markup-resource-stream-properties
description: When a MergedMarkup wraps another Markup, it must copy resource stream
  properties (encoding, xml declaration, wicket namespace). Tests should verify these
  properties are preserved and independent for each merged instance.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
- MERGE_STRATEGY_OVERRIDE
test_pattern: STATE_TEST
---

# merged-markup-resource-stream-properties

## Instructions

# MergedMarkup Resource Stream Property Propagation

## Instructions

- WHEN a class acts as a decorator/merger that wraps another object (e.g., `MergedMarkup` wrapping a `Markup`) — THEN the test MUST verify that ALL resource stream properties from the wrapped object are properly propagated to and accessible from the wrapper.
  
- WHEN testing `MergedMarkup` (or similar merger classes) — THEN create a test that:
  1. Creates a `MarkupResourceStream` with known values for `getEncoding()`, `getXmlDeclaration()`, and `getWicketNamespace()` 
  2. Wraps it in a `MergedMarkup` 
  3. Calls `mergedMarkup.getMarkupResourceStream().getEncoding()`, `mergedMarkup.getMarkupResourceStream().getXmlDeclaration()`, and `mergedMarkup.getMarkupResourceStream().getWicketNamespace()` 
  4. Asserts the values match the original
  5. ALSO tests that modifying the original does NOT affect the wrapper (defensive copy)

- WHEN the merger's constructor takes `(Markup markup, int caretLineNumber)` — THEN verify that `markup.getMarkupResourceStream()` is handled properly (not null, not lost). If the original `Markup` has a non-null `MarkupResourceStream`, the `MergedMarkup` must also return a non-null `MarkupResourceStream` with the same properties.

- Common pitfalls to avoid:
  - Testing only markup content (tags/text) without testing resource stream metadata properties
  - Assuming properties like `encoding`, `xmlDeclaration`, `wicketNamespace` are inherited automatically from the parent class
  - Testing with a mock or stub that doesn't set real resource stream properties
  - Forgetting to test both: (a) that properties exist on the merged object, and (b) that they match the original wrapped object's values

### Correct Test Pattern (Java/JUnit):
```java
// Create a real MarkupResourceStream with known properties
MarkupResourceStream resourceStream = new MarkupResourceStream(...);
resourceStream.setEncoding("UTF-16");
resourceStream.setXmlDeclaration(new XmlDeclaration("1.0", "UTF-16", null));
resourceStream.setWicketNamespace("w");

// Create a Markup that uses this resource stream  
IMarkup markup = new SomeMarkupImplementation(resourceStream);

// Wrap in MergedMarkup
MergedMarkup merged = new MergedMarkup(markup, 1);

// Assert properties are propagated
MarkupResourceStream mergedStream = merged.getMarkupResourceStream();
assertNotNull("MergedMarkup must have a MarkupResourceStream", mergedStream);
assertEquals("UTF-16", mergedStream.getEncoding());
assertNotNull("XmlDeclaration must be propagated", mergedStream.getXmlDeclaration());
assertEquals("w", mergedStream.getWicketNamespace());
```

### Incorrect Test Pattern (common pitfall):
```java
// Only tests markup tags/content, ignoring resource stream properties
MergedMarkup merged = new MergedMarkup(someMarkup, 1);
// Missing assertions for encoding, xmlDeclaration, wicketNamespace
// Just testing getMarkupResourceStream() != null is not enough
```