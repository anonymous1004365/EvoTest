---
name: error-handler-header-preservation-with-onprepare
description: When an error handler (e.g., DeadLetterChannel) uses onPrepareProcessor,
  the processor must be invoked before the exchange is sent to the dead letter queue.
  Without this, custom headers set by onPrepare are lost. Test that headers set in
  onPrepare are present in the dead letter / error exchange.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ERROR_HANDLER_HEADER_PRESERVATION
test_pattern: INTERACTION_TEST
---

# error-handler-header-preservation-with-onprepare

## Instructions

# Error Handler Header Preservation with onPrepareProcessor

## Instructions

- WHEN the TG encounters an error handler (e.g., `DeadLetterChannel`, `RedeliveryErrorHandler`) that configures a **`onPrepareProcessor`** to run before the exchange is sent to the dead letter endpoint  
  AND the `onPrepareProcessor` sets headers or properties on the exchange (e.g., `exchange.getOut().setHeader("foo", ...)`)
- THEN the TG must write a test that verifies the **dead letter queue receives the exchange with those headers intact**. Specifically:
  1. Route: start → a processor that **throws an exception** (e.g., `throw new RuntimeException("forced")`) → end
  2. Error handler: `DeadLetterChannel("mock:error")` with `onPrepareProcessor` that adds a header (e.g., `"foo"`)
  3. Mock endpoint `mock:error` expects `header("foo").isNotNull()` (i.e., the header set by onPrepare must survive the error routing)
  4. Send one message into the route and verify the mock receives the expected header
  5. If the bug is present, the header is cleared/dropped; the test will fail with something like `No header with name foo found for message: 0`
- **Common pitfalls**:
  - ❌ Testing only that the dead letter queue receives the message (without checking the header)
  - ❌ Forgetting to use `getOut()` in the onPrepareProcessor (the header must be set on the **out** message for Camel error handlers to propagate it)
  - ❌ Using `Exchange.CHARSET_NAME` or `Exchange.CONTENT_TYPE` as the header value – it must be a **custom header** that is not preserved by the error handler's default behavior

### Example (correct)
```java
RouteBuilder builder = new RouteBuilder() {
    public void configure() {
        errorHandler(deadLetterChannel("mock:error")
            .onPrepareProcessor(exchange -> {
                // set the header on the OUT message
                exchange.getOut().setHeader("foo", "bar");
            }));
        from("direct:start")
            .process(exchange -> {
                throw new RuntimeException("forced");
            });
    }
};
template.sendBody("direct:start", "Hello");
mockEndpoint.assertIsSatisfied();  // mock:error expects header("foo")
```

### Example (incorrect)
```java
// ❌ Only tests that the exchange arrives at the dead letter queue,
//    does NOT verify that the header set by onPrepareProcessor is preserved.
RouteBuilder builder = new RouteBuilder() {
    public void configure() {
        errorHandler(deadLetterChannel("mock:error"));
        from("direct:start")
            .process(exchange -> {
                throw new RuntimeException("forced");
            });
    }
};
template.sendBody("direct:start", "Hello");
mockEndpoint.expectedMessageCount(1);  // passes even if header is lost
```