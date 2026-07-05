---
name: stream-body-formatting-with-showstreams
description: When formatting messages with showStreams enabled, test that InputStream
  body content is correctly converted to string representation. Use this skill when
  testing logging or formatting components that handle stream-based message bodies.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- VALIDATION
- STREAM_HANDLING
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# stream-body-formatting-with-showstreams

## Instructions

# Stream Body Formatting with showStreams

## Instructions

- WHEN the TG encounters a formatter that has a `showStreams` option (boolean flag controlling whether to show stream content as string vs just `<InputStream>`) AND the formatter's `getBodyAsString(Message)` or similar method is used to convert message body to string for output
- THEN the TG should write a test that:
  1. Creates an exchange with an `InputStream` body (e.g., `new ByteArrayInputStream("Hello World".getBytes())`)
  2. Sets `showStreams = true` on the formatter
  3. Calls the formatting method (e.g., `formatExchange(exchange, sb, "IN")`)
  4. Verifies the body content appears in the formatted output string (e.g., `sb.toString()` contains `"Hello World"`)
  5. On the buggy version, the formatted output would contain empty string or `""` where the body text should be, or show the unhelpful `[Body is instance of java.io.InputStream]` representation instead of the actual stream content

- Common pitfalls to avoid:
  - Testing only with String-type message bodies instead of InputStream bodies
  - Not verifying the string conversion of the InputStream body appears in the output
  - Not resetting the InputStream after reading (in the fixed version, the stream should be reset with `mark()`/`reset()` so the exchange is not consumed)
  - Testing `showStreams=true` only in isolation without verifying the formatted output via `sb.toString()`
  - Assuming `getBodyAsString()` works the same for all message body types

- Correct test example:
```java
// Buggy version: getBodyAsString() returns "" for InputStream because InputStream is not processed
// Fixed version: getBodyAsString() properly reads InputStream and resets it
@Test
public void testStreamBodyInLog() throws Exception {
    DefaultExchangeFormatter formatter = new DefaultExchangeFormatter();
    formatter.setShowStreams(true);
    
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setBody(new ByteArrayInputStream("Hello World".getBytes()));
    
    StringBuilder sb = new StringBuilder();
    formatter.formatExchange(exchange, sb, "IN");
    
    String output = sb.toString();
    assertTrue("Body text should appear in output", output.contains("Hello World"));
}
```

- Incorrect test example:
```java
// BAD: Only tests String body, not InputStream body
@Test
public void testLogBody() throws Exception {
    DefaultExchangeFormatter formatter = new DefaultExchangeFormatter();
    formatter.setShowStreams(true);
    
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setBody("Hello World");  // String, not InputStream
    
    StringBuilder sb = new StringBuilder();
    formatter.formatExchange(exchange, sb, "IN");
    
    // This test passes even on buggy version because String works fine
    String output = sb.toString();
    assertTrue("Body text should appear in output", output.contains("Hello World"));
}
```