---
name: log-eip-exception-propagation
description: When a Log EIP (LogProcessor) processes a route, exceptions thrown during
  logging (e.g., by LogListeners) must propagate back to the Exchange to trigger error
  handling. Use this skill when testing custom log listeners or logging processors
  that can throw exceptions.
code_tags:
- EXCEPTION_HANDLING
test_pattern: INTERACTION_TEST
---

# log-eip-exception-propagation

## Instructions

# Log EIP Exception Propagation

## Instructions

- WHEN the TG encounters a custom `LogListener` implementation that can throw a `Throwable` during the `onLog` callback, OR when a `LogProcessor` or `CamelLogProcessor` is used in a route with the `log` EIP
- THEN the TG should verify that exceptions thrown inside the `LogListener.onLog()` method are not silently swallowed but instead propagate back to the `Exchange` via `exchange.setException()` or `exchange.setProperty(Exchange.EXCEPTION_CAUGHT, ...)`, so that Camel's error handling can route the exchange to a dead letter channel or error handler
- THEN the TG should write a test that:
  1. Creates a custom `LogListener` whose `onLog()` method throws a specific exception (e.g., `throw new RuntimeException("forced")`)
  2. Adds this listener to the `CamelContext` via `context.addLogListener(listener)`
  3. Defines a route that uses `.log(LoggingLevel.ERROR, "...")` such that when the exchange reaches the `log` EIP, the listener's `onLog()` is invoked
  4. Sets up an error handler (e.g., `deadLetterChannel("mock:exceptionFailure")`) to catch the exception from the failed exchange
  5. Sends a message to the route and asserts that the exchange ended up in the dead letter channel (e.g., `mock:exceptionFailure.expectedMessageCount(1)`)
- THEN the TG should verify that in the **buggy** version, the exchange is **not** routed to the error handler (i.e., mock receives 0 messages), confirming that the exception was silently swallowed. In the **fixed** version, the exception is properly propagated and the exchange appears in the error handler mock (1 message).

### Common pitfalls to avoid

- **Testing only happy-path logging**: Do not assume that logging is side-effect-free. If a `LogListener` can throw, test that the exception propagates.
- **Assuming `log()` is always safe**: The `log` EIP is both a logging statement and a processor step. An exception during logging must behave like any other processor exception: it should trigger error handling.
- **Using `shouldLog()` as a guard assumption**: Do not assume that checking `logger.shouldLog()` before calling `fireListeners()` makes the code safe. If `shouldLog()` returns true and the listener throws, the exception must still propagate.
- **Forgetting to set up an error handler**: Without `deadLetterChannel(...)` or similar, the default error handling may silently drop exceptions. Always configure an explicit error handler in the test to observe propagation.

### Correct example (what the TG should write)

```java
// Custom LogListener that throws
public class ThrowingLogListener implements LogListener {
    @Override
    public String onLog(Exchange exchange, CamelLogger logger, String message) {
        throw new RuntimeException("forced");
    }
}

// Route with error handler
context.addLogListener(new ThrowingLogListener());

context.getRouteDefinitions().clear();
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() {
        errorHandler(deadLetterChannel("mock:exceptionFailure"));
        from("direct:start").log(LoggingLevel.ERROR, "Logging message");
    }
});

template.sendBody("direct:start", "Hello World");
mockExceptionFailure.expectedMessageCount(1);
mockExceptionFailure.assertIsSatisfied();
```

### Common mistake to avoid (what the TG might write incorrectly)

```java
// WRONG: Testing only that logging works, not that exceptions propagate
// This test would pass on both buggy and fixed versions
context.addLogListener((exchange, logger, message) -> message.toUpperCase());

context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() {
        from("direct:start")
            .log(LoggingLevel.ERROR, "Logging ${body}")
            .to("mock:result");
    }
});

template.sendBody("direct:start", "hello");
mockResult.expectedMessageCount(1);  // passes on both versions, doesn't detect the bug
mockResult.assertIsSatisfied();
```