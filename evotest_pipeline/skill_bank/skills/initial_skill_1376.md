---
name: filename-extension-splitting-parsing
description: When a utility method uses String.split(".") or String.split(regex) to
  parse filename extensions, test that filenames with multiple dots (e.g., "test.file.rf")
  are handled correctly and the correct extension-based dispatch occurs.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# filename-extension-splitting-parsing

## Instructions

# Filename Extension Splitting and Parsing

## Instructions

- WHEN the TG encounters code that uses `String.split(".")` or `String.split("\\.")` to parse a filename's extension (e.g., extracting the suffix after the last dot in a filename like "table.rf" or "test.file.rf")
- THEN the TG should write a test that provides a filename containing **more than one dot** (e.g., `"test.file.rf"`) and verify that the extension is correctly identified as the part after the **last** dot (e.g., `"rf"`) — not the part after the first dot (e.g., `"file.rf"` or `"file"`)
- Include concrete examples: filenames like `"test.file.rf"`, `"a.b.c.map"`, `"some.prefix.file.rf"` where the last segment is the true extension
- Verify that the method correctly dispatches or processes based on the **last** segment (the true extension), and that it does not throw an exception or return an incorrect result on such inputs
- Common pitfalls to avoid:
  - Testing only single-dot filenames (e.g., `"table.rf"`), which passes buggy code that splits on every dot instead of finding the last one
  - Using `String.split(".")` (which matches any character) instead of properly escaping with `String.split("\\.")` — though even proper splitting needs to take the **last** segment, not just split and take index [1]
  - Assuming the extension is always the second segment after splitting on dot — for filenames like `"a.b.c.rf"`, splitting on dot gives `["a", "b", "c", "rf"]`, so index [3] is the extension, not index [1]

### Correct Example

```java
@Test
public void testMultipleDotsInFilename() {
    String filename = "test.file.rf";
    // The correct behavior: the method should identify "rf" as the extension
    // and dispatch accordingly (e.g., open an RFile writer/reader)
    FileOperations ops = FileOperations.getInstance();
    // Verify no exception is thrown and correct operation is performed
    assertDoesNotThrow(() -> ops.openWriter(filename, ...));
}
```

### Incorrect Example (would pass buggy code)

```java
@Test
public void testSingleDotFilename() {
    String filename = "table.rf";
    // This test would pass even with buggy code that only handles single-dot filenames
    // because splitting "table.rf" on "." gives ["table", "rf"] — extension at index [1] works
    FileOperations ops = FileOperations.getInstance();
    assertDoesNotThrow(() -> ops.openWriter(filename, ...));
}
```