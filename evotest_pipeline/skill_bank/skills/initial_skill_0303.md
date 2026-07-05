---
name: parameterized-message-body-handling
description: When testing layouts or formatters that convert LogEvent message bodies,
  always test with parameterized Message objects (not just StringMessage) to verify
  the formatted body is the resolved string, not the raw template. This skill catches
  bugs where layouts fail to call Message.getFormattedMessage().
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# parameterized-message-body-handling

## Instructions

# Parameterized Message Body Handling

## Instructions

- WHEN testing a layout, appender, or formatter that extracts the message body from a LogEvent via `event.getMessage().getFormat()` or `event.getMessage().toString()` rather than `event.getMessage().getFormattedMessage()`
- THEN the TG MUST write a test that submits a **parameterized Message** (e.g., `new ParameterizedMessage("Hello {}", "World")`) and verifies the output contains the **resolved/rendered message** (e.g., `"Hello World"`), NOT the raw template (e.g., `"Hello {}"`).
- The test should:
  1. Create a `ParameterizedMessage` with a format string and arguments, e.g., `new ParameterizedMessage("Hello {}", "World")`
  2. Wrap it in a `LogEvent` (e.g., `Log4jLogEvent.newBuilder().setMessage(msg).build()`)
  3. Pass the event through the layout's `toSerializable(LogEvent)` or `encode(LogEvent, ByteBuffer)` method
  4. Assert that the output string contains the **formatted message** (e.g., `contains("Hello World")`)
  5. Assert that the output does NOT contain the raw placeholder (e.g., `not(contains("Hello {}"))`)
  6. Optionally, verify the output against a full expected string literal
- Common pitfalls to avoid:
  - **Only testing with `StringMessage` (simple strings)**: A `new SimpleMessage("Hello World")` will pass even if `getFormat()` is used, because `getFormat()` returns the same string. Always test with a `ParameterizedMessage` or `FormattedMessage`.
  - **Testing only via `LogEvent.getMessage()` in isolation**: The bug may only manifest when the layout serializes the event. Test the full layout pipeline end-to-end.
  - **Checking only partial substrings**: The buggy behavior might output the raw template plus some prefix/suffix. Assert the **exact expected output** when possible.
  - **Assuming the layout class is correct**: Even well-tested layout classes may have this bug in new methods or overloaded variants.

### Correct Test Example (What the TG SHOULD write)

```java
@Test
public void testParameterizedMessage() {
    final Message msg = new ParameterizedMessage("Hello {}", "World");
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("test")
        .setLevel(Level.INFO)
        .setMessage(msg)
        .build();
    final String result = layout.toSerializable(event);
    assertThat(result, containsString("Hello World"));
    assertThat(result, not(containsString("Hello {}")));
    // Full expected output example:
    // "<134>1 2016-07-16T13:41:06.433-07:00 D3118-A1 ATM - - - Hello World"
}
```

### Incorrect Test Example (What the TG might write without this skill)

```java
// WRONG: Only tests with SimpleMessage — passes even on buggy version
@Test
public void testSimpleMessage() {
    final Message msg = new SimpleMessage("Hello World");
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setMessage(msg)
        .build();
    final String result = layout.toSerializable(event);
    assertThat(result, containsString("Hello World"));
}
```