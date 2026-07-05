---
name: bracket-not-interpolated-message-handling
description: When logging messages contain literal curly braces that are NOT interpolation
  placeholders, the MessagePatternConverter must not attempt interpolation, which
  can cause unterminated-bracket errors. Use this skill to test that messages with
  unbalanced or literal curly braces are formatted as plain text without interpolation
  exceptions.
code_tags:
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: EXCEPTION_TEST
---

# bracket-not-interpolated-message-handling

## Instructions

# Bracket In Non-Interpolated Message Handling

## Instructions

- WHEN the TG encounters a `MessagePatternConverter` (or similar pattern-based converter) that processes messages containing curly braces (`{` or `}`) which are NOT part of interpolation syntax (e.g., `{}` or `{n}` placeholders)
- THEN the TG should test messages that contain literal curly braces (e.g., `"This is a { message with brackets"` or `"Message with } bracket"`) and verify that:
  1. The message is output as plain text without any interpolation attempt
  2. No exception (e.g., `IllegalArgumentException`, `ArrayIndexOutOfBoundsException`, `StringIndexOutOfBoundsException`) is thrown during formatting
  3. The output exactly matches the input string (the message is not modified)
- The TG should specifically test messages that have:
  - A single opening brace without a closing brace: `"Issue: { bug"`
  - A single closing brace without an opening brace: `"Bug: } issue"`
  - Unmatched braces with other content: `"Error: {0} missing { parameter"`
- Common pitfalls to avoid:
  - Testing only balanced braces that look like parameter placeholders (e.g., `"Error: {}"` and `"Error: {0}"`)
  - Assuming that all curly braces in messages are interpolation placeholders
  - Not testing with the Format specifier `noLookups` (if applicable) or testing only with default converter settings
  - Testing only `StringMessage` type messages but not `SimpleMessage` or `ParameterizedMessage` types

### Example (correct test approach)

```java
@Test
public void testLiteralBracketInMessage() {
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("TestLogger")
        .setLevel(Level.INFO)
        .setMessage(new SimpleMessage("This is a { message with bracket"))
        .build();
    final StringBuilder sb = new StringBuilder();
    converter.format(event, sb);
    assertEquals("This is a { message with bracket", sb.toString());
}

@Test
public void testClosingBracketInMessage() {
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("TestLogger")
        .setLevel(Level.INFO)
        .setMessage(new SimpleMessage("Message with } bracket"))
        .build();
    final StringBuilder sb = new StringBuilder();
    converter.format(event, sb);
    assertEquals("Message with } bracket", sb.toString());
}
```

### Example (incorrect approach — only tests balanced braces)

```java
@Test
public void testOnlyBalancedBrackets() {
    // This misses the bug because both braces are balanced
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setMessage(new SimpleMessage("No interpolation {} here"))
        .build();
    // ... format and verify ...
}
```