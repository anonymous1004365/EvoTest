---
name: json-escape-double-quote-handling
description: When generating JSON output, strings containing double quotes (") must
  be properly escaped as \" to produce valid JSON. This skill applies when a layout/formatter
  writes JSON-encoded log messages or any JSON string values.
code_tags:
- ESCAPE_PROCESSING
test_pattern: PARAMETRIC_TEST
---

# json-escape-double-quote-handling

## Instructions

# JSON String Double-Quote Escaping in Layouts

## Instructions

### WHEN the TG encounters code that generates JSON output by writing string values (e.g., log message content in a JSON layout):

- **WHEN** a `JsonLayout`, `AbstractJacksonLayout`, or similar JSON-generation class writes string field values (e.g., message, level, timestamp) to output — especially when it manually concatenates or formats strings rather than using a JSON library serializer
- **THEN** the TG should write a **parametric test** that verifies proper escaping of special characters, particularly **double quotes (`"`) and single quotes (`'`)** inside string values
- **What to verify**: The test should confirm that:
  - A double quote character (`"`) inside a log message is escaped as `\"` in the JSON output
  - A single quote character (`'`) inside a log message is not broken or incorrectly escaped
  - The JSON remains syntactically valid (e.g., the generated string can be parsed as valid JSON)
- **What exception/error to expect on the buggy version**: On the buggy version, the generated JSON has unescaped double quotes, causing the JSON value to be prematurely terminated and an `AssertionError` when comparing expected vs actual output lines, e.g., `"message":"Here is a quote ' and then a double quote "","` where `""` after the quote breaks the JSON structure

### Common pitfalls to avoid:

1. **Testing only with plain text**: A test with a simple message like "Hello" will NOT catch escape bugs. Always include special JSON characters.
2. **Testing only single quotes**: Single quotes (`'`) are valid in JSON without escaping; testing them alone won't trigger the bug. Use double quotes (`"`) as the primary trigger.
3. **Testing only escape sequences from other formats**: Testing `\n` or `\t` escaping is a different concern. This bug specifically relates to **double quotes** (`"`) not being escaped.
4. **Assuming JSON library handles everything**: If the code manually writes JSON string values (concatenating `"message":""` with the raw message), the escape bug lies in the pre-processing — test it directly.
5. **Checking partial output only**: Assert on complete lines of JSON output, not just substrings, to catch structural breakage.

### Example (correct test pattern):

```java
// CORRECT: Tests that double quotes in messages are properly escaped
@Test
public void testEscapeDoubleQuotesInMessage() throws Exception {
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("test")
        .setLevel(Level.INFO)
        .setMessage(new SimpleMessage("Here is a quote ' and then a double quote \""))
        .setThreadName("main")
        .setTimeMillis(System.currentTimeMillis())
        .build();
    
    final AbstractJacksonLayout layout = JsonLayout.newBuilder()
        .setLocationInfo(false)
        .setProperties(false)
        .setComplete(false)
        .setCompact(true)
        .setCharset(StandardCharsets.UTF_8)
        .build();
    
    final String result = layout.toSerializable(event);
    // The double quote must be escaped
    assertTrue("Double quote should be escaped", result.contains("\\\""));
    // The JSON structure should not break
    assertTrue("Message field should be complete", 
        result.matches(".*\"message\":\".*\\\\\".*\".*"));
}
```

### Example (incorrect test pattern — will NOT catch this bug):

```java
// INCORRECT: Only tests a simple non-escaping message — won't catch the bug
@Test
public void testSimpleMessage() throws Exception {
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setMessage(new SimpleMessage("Hello World"))  // No special characters!
        // ...
        .build();
    
    final String result = layout.toSerializable(event);
    assertTrue(result.contains("Hello World"));  // Passes even with the bug
}
```