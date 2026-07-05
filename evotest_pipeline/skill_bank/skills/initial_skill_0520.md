---
name: xml-complete-indentation-validation
description: WHEN a layout produces complete (well-formed) XML output with child elements
  that should be indented relative to the root, THEN validate that all child Event
  elements have proper two-space indentation and nested Message elements have four-space
  indentation, because the PrettyPrinter nesting level affects indentation of non-root
  elements.
code_tags:
- STATE_MUTATION
- XML_SERIALIZATION_INDENTATION
test_pattern: STATE_TEST
---

# xml-complete-indentation-validation

## Instructions

# XML Complete Output Indentation Validation

## Instructions

**WHEN** the TG encounters an `XmlLayout` (or `AbstractJacksonLayout` subclass) configured with `complete="true"` (i.e., producing a well-formed XML document with a root `<Events>` element), **THEN** it should write a test that:

1. **Logs multiple events** (at least two) to an XML file using a file appender with `immediateFlush="false"`.
2. **Stops the logger context** to flush all pending events to disk.
3. **Reads the output file line by line** and validates indentation of each XML element line:
   - The XML declaration and `<Events>` root element must have **zero indentation** (not start with a space).
   - Each `<Event>` element must start with **exactly two spaces** (`"  "`), not more.
   - Each nested child element (e.g., `<Message>`) inside an `<Event>` must start with **exactly four spaces** (`"    "`), not more.
   - Each `</Event>` closing tag must start with **exactly two spaces** (`"  "`), not more.
   - The `</Events>` closing tag must have **zero indentation**.
4. **Assert the content** of each line contains the expected log message text.
5. **Delete the log file** after verification in a `finally` block.

**Common pitfalls to avoid:**
- Testing only with a single event: the bug manifests when multiple events are written to the same file, as the PrettyPrinter's `createInstance()` method can reset the nesting level. Test with at least two log events.
- Testing only the content of elements without checking indentation: verify both content AND leading whitespace.
- Using `immediateFlush="true"` or not stopping the async logger context: this may prevent the file from being fully written before reading.
- Assuming the first `<Event>` is indented the same as later `<Event>` elements: the bug causes inconsistent indentation across multiple events.

**Correct test pattern (Java):**
```java
@Test
public void testChildElementsAreCorrectlyIndented() throws Exception {
    final Logger logger = this.loggerContextRule.getLogger("com.foo.Bar");
    logger.info("First message");
    logger.info("Second message");
    CoreLoggerContexts.stopLoggerContext(false, logFile);
    
    try (final BufferedReader reader = new BufferedReader(new FileReader(logFile))) {
        String line;
        int lineIndex = 0;
        while ((line = reader.readLine()) != null) {
            if (!"".equals(line.trim())) {
                // line 0: <?xml...> - no indent
                // line 1: <Events ...> - no indent
                // line 2+: <Event ...> - two-space indent
                // ...
                if (lineIndex == 0 || lineIndex == 1) {
                    assertFalse("Line " + lineIndex + " must not be indented", line.startsWith(" "));
                } else if (/* Event line */) {
                    assertTrue("Event line must have 2-space indent", line.startsWith("  "));
                    assertFalse("Event line must not have more than 2-space indent", line.startsWith("   "));
                }
                lineIndex++;
            }
        }
    }
}
```

**Incorrect test pattern (what would miss the bug):**
```java
// BAD: Only checks content, not indentation
assertTrue(line.contains("<Event"));
// BAD: Only logs one event
logger.info("Single message");
// BAD: Doesn't check that indentation is exactly 2 spaces, just checks it isn't at column 0
assertFalse(line.startsWith(" ")); // this is actually wrong for Event lines!
```