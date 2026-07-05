---
name: parser-auto-close-behavior
description: When testing YAML/JSON parsers with auto-close disabled, ensure the test
  verifies that a reader/input stream passed to the parser factory remains open after
  the parser is closed. This skill checks for resource lifecycle bugs where closing
  the parser incorrectly closes the underlying reader.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- VALIDATION
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: STATE_TEST
---

# parser-auto-close-behavior

## Instructions

# Parser Auto-Close Behavior Validation

## Instructions

- WHEN the TG encounters a `JsonParser` or `YAMLParser` factory method that accepts a `Reader`, `InputStream`, or other closeable resource AND has an auto-close feature or flag (e.g., `JsonParser.Feature.AUTO_CLOSE_SOURCE`) that controls whether the parser closes the underlying resource upon its own close
- THEN the TG should write a test that:
  1. Creates a non-auto-closeable reader/resource (wrapping a `StringReader` / `ByteArrayInputStream` etc.)
  2. Passes it to the parser factory method (e.g., `YAMLFactory().createParser(reader)`)
  3. Configures the parser to NOT auto-close (e.g., `parser.disable(JsonParser.Feature.AUTO_CLOSE_SOURCE)`)
  4. Reads or parses all tokens from the parser
  5. Calls `parser.close()`
  6. **Verifies that the underlying reader/resource is still open** (e.g., `assertTrue(reader.ready())` or `assertDoesNotThrow(() -> reader.read())`)
  - The test must catch the case where closing the parser incorrectly/silently closes the underlying resource even when auto-close is disabled.
  - Expected behavior on the buggy version: The underlying reader/resource IS (incorrectly) closed by `parser.close()`, and `reader.ready()` may return false or throw an IOException.
  - Expected behavior on the fixed version: The underlying reader/resource remains open and readable after `parser.close()`.

- Common pitfalls to avoid:
  - Testing only with String input via `readValue()` or tree model — this bypasses the parser's resource handling code path.
  - Forgetting to explicitly configure `disable(AUTO_CLOSE_SOURCE)` — the default may be to auto-close.
  - Creating a `StringReader` but not verifying it remains usable after parser close.
  - Testing only that the parser produces correct tokens without checking the resource lifecycle.
  - Using `try-with-resources` on the reader — that would close it automatically and defeat the test purpose.

## Example

Consider this buggy code in a class like `YAMLParser` or `ReaderBasedJsonParser`:

```java
// Buggy: Closing the parser always closes the underlying reader,
// ignoring the AUTO_CLOSE_SOURCE setting
@Override
public void close() throws IOException {
    super.close();
    _reader.close();  // BUG: should check if AUTO_CLOSE_SOURCE is enabled first
}
```

A correct test to catch this bug:

```java
@Test
public void testParseReaderWithoutAutoClose() throws Exception {
    String yaml = "key: value\n";
    StringReader reader = new StringReader(yaml);
    YAMLFactory factory = new YAMLFactory();
    JsonParser parser = factory.createParser(reader);
    parser.disable(JsonParser.Feature.AUTO_CLOSE_SOURCE);

    // Fully read/parse the document
    while (parser.nextToken() != null) {
        // consume all tokens
    }

    // Close the parser
    parser.close();

    // Verify the underlying reader is still open
    // On the buggy version, this would fail — reader is closed
    assertTrue("Reader should still be open after parser close with AUTO_CLOSE_SOURCE disabled",
        reader.ready());
    // Also verify we can still read from the reader
    assertEquals('k', reader.read());  // should still work
}
```

An incorrect test that would NOT catch this bug:

```java
@Test
public void testParseReaderWithoutAutoClose_WRONG() throws Exception {
    // WRONG: using try-with-resources on the reader
    // This hides whether the parser closes the reader or not
    try (StringReader reader = new StringReader("key: value\n")) {
        JsonParser parser = new YAMLFactory().createParser(reader);
        parser.disable(JsonParser.Feature.AUTO_CLOSE_SOURCE);
        while (parser.nextToken() != null) { }
        parser.close();
    }
    // No assertion on reader state — bug would go undetected
}
```