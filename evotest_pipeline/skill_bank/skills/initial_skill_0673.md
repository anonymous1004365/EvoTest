---
name: xml-complete-layout-indentation
description: When testing XML layouts with Jackson serialization, verify that child
  elements nested inside a root XML element are indented even when the complete="true"
  attribute is used to produce a standalone XML document.
code_tags:
- VALIDATION
- STATE_MUTATION
- XML_INDENTATION_PRETTY_PRINTING
test_pattern: STATE_TEST
---

# xml-complete-layout-indentation

## Instructions

# XML Complete Layout Indentation

## Instructions

- WHEN the Test Generator encounters a layout configuration using `XMLLayout` with `complete="true"` (producing a standalone XML document with XML declaration and root `<Events>` element)
- THEN the TG should verify that **child elements nested inside the root element are properly indented** (each line of child content should have two-space indentation relative to the root element)
- Specifically, test that the output file contains lines with leading whitespace (two spaces) before child elements such as `<Event ...>` or `<Event xmlns=...>`
- The test should verify that the XML output is **pretty-printed** (indented) even when `complete="true"` is set and `compact` is not explicitly set to `true`
- The test should verify output using assertions on specific line content (e.g., `assertTrue("line 3 incorrect: " + line3, line3.startsWith("  <Event"))` )
- Common pitfall: Testing only that the XML declaration `<?xml version="1.0" encoding="UTF-8"?>` and root element `<Events>` are present, but forgetting to verify that child elements like `<Event>` have indentation. The bug is that child elements lack indentation (appear as `startOfLine<Event...>` instead of `  <Event...>`).

### Correct test approach:
```java
@Test
public void testChildElementsAreCorrectlyIndented() {
    final String line3 = Files.readAllLines(logFile.toPath()).get(2);
    assertTrue("line 3 must have indentation: " + line3, line3.startsWith("  <Event"));
}
```

### Incorrect test approach:
```java
@Test
public void testCompleteXmlLayout() {
    final String content = new String(Files.readAllBytes(logFile.toPath()));
    assertTrue(content.contains("<Events>"));      // only checks root element
    assertTrue(content.contains("<Event"));         // only checks child exists
    // MISSING: verifying that child elements are indented
}
```