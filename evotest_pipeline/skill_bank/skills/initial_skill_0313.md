---
name: stream-cache-reset-on-use-original-message
description: When testing error handling with useOriginalMessage() and a StreamCache
  body, verify that the stream is properly reset so the original body content can
  be read from the exception handler. This is critical when the body is consumed (e.g.,
  getBody(String.class)) in the route before the error occurs.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- STATE_MUTATION
- STREAM_RESET_MARK
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# stream-cache-reset-on-use-original-message

## Instructions

# Stream Cache Reset After Error Handling with useOriginalMessage

## Instructions

- WHEN the TG encounters code that uses `.useOriginalMessage()` in an `onException` clause AND the message body is a `StreamCache` implementation (e.g., `InputStreamCache`, `ByteArrayInputStreamCache`, `FileInputStreamCache`), THEN the TG should write a test that sends a `StreamCache` body through a route where:
  1. The body is consumed (e.g., via `getBody(String.class)` in a processor) before an exception is thrown
  2. The `onException` clause marks the exception as `handled(true)` and routes to a separate endpoint
  3. The test asserts that the original `StreamCache` body content can be read (e.g., `getBody(String.class)`) from the exchange at the error-handling endpoint, proving the stream was properly reset

- WHEN a `StreamCache` body is read via `getBody(String.class)`, the internal stream position advances. If the stream is not reset before the error handler accesses the "original" message body, reading from it will return empty content. The test MUST verify that the content from the error endpoint equals the original sent content, not empty or truncated.

- The test should use concrete types like `org.apache.camel.converter.stream.InputStreamCache` to construct the body with known byte content (e.g., `new InputStreamCache("<firstName>James</firstName>".getBytes())`).

- After `assertMockEndpointsSatisfied()`, the test MUST retrieve the exchange from the error-handling mock endpoint and call `getBody(String.class)` to verify the content contains the expected original string.

- Common pitfalls to avoid:
  - Testing only with `String` bodies (which are not `StreamCache`) — this won't reproduce the stream-not-reset bug
  - Testing only that the error handler receives the message without verifying the body content
  - Asserting the body by reference equality — the stream cache wraps bytes, so assert on content equality

- Example correct test pattern:
  ```java
  InputStreamCache cache = new InputStreamCache(TEST_STRING.getBytes());
  template.sendBody("direct:a", cache);
  assertMockEndpointsSatisfied();
  String result = getMockEndpoint("mock:error").getExchanges().get(0).getIn().getBody(String.class);
  assertTrue("Should contain original content", result.contains("<firstName>James</firstName>"));
  ```

- Example incorrect test pattern:
  ```java
  template.sendBody("direct:a", "Hello World");
  assertMockEndpointsSatisfied();
  // Missing: verifying that body content is intact after stream consumption + error handling
  ```