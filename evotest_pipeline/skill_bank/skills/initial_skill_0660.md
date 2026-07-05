---
name: idempotent-consumer-null-message-id-testing
description: When testing routes with idempotentConsumer that use message ID expressions,
  test what happens when the expression evaluates to null — the IdempotentConsumer
  processor should set a NoMessageIdException on the exchange and route it to the
  dead letter channel. This skill helps you write tests that verify proper error handling
  for missing message IDs in idempotent consumer routes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# idempotent-consumer-null-message-id-testing

## Instructions

# Test Idempotent Consumer Behavior When Message ID Expression Evaluates to Null

## Instructions

WHEN you encounter an `idempotentConsumer` DSL method (from `org.apache.camel.model.IdempotentConsumerDefinition`) that uses a message ID expression (e.g., `header("messageId")`, `body()`, or any custom `Expression`) combined with an `IdempotentRepository`,

THEN you must write a test that sends at least one exchange **without** the header/field that the message ID expression evaluates, and verify the following:
- The exchange is NOT processed by the main route endpoint (e.g., `mock:result`).
- The exchange IS routed to the dead letter channel endpoint (e.g., `mock:dead`).
- The exchange has a `NoMessageIdException` (`org.apache.camel.processor.idempotent.NoMessageIdException`) set as its exception.
- Do NOT use `expectedException` or `@Test(expected=...)` — the exception is set on the exchange (via `exchange.setException()`), NOT thrown out of the route. The route continues to the error handler.

### Concrete example from the actual bug:

The route under test:
```java
from("direct:start").idempotentConsumer(
    header("messageId"), MemoryIdempotentRepository.memoryIdempotentRepository(200)
).to("mock:result");
```

The triggering test sends a message **without** the `messageId` header:
```java
public void testNoMessageId() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            errorHandler(deadLetterChannel("mock:dead"));
            from("direct:start").idempotentConsumer(
                header("messageId"), MemoryIdempotentRepository.memoryIdempotentRepository(200)
            ).to("mock:result");
        }
    });
    context.start();

    resultEndpoint.expectedBodiesReceived("one", "two");
    getMockEndpoint("mock:dead").expectedBodiesReceived("Hello World");

    sendMessage("1", "one");
    template.sendBody("direct:start", "Hello World");  // <-- no "messageId" header!
    sendMessage("2", "two");
    sendMessage("1", "one");

    assertMockEndpointsSatisfied();
}
```

### Common pitfalls to avoid:

1. **DO NOT** use `@Test(expected = NoMessageIdException.class)` — the exception is set on the exchange, not thrown. Using expected will cause the test to fail.
2. **DO NOT** assert that the mock:result endpoint receives the message without the message ID — it should go to the dead letter channel, not the result endpoint.
3. **DO NOT** forget to configure an `errorHandler(deadLetterChannel(...))` — otherwise the exchange may be handled by the default error handler and not reach your expected dead letter endpoint.
4. **DO NOT** test only with valid message IDs — the null/absent message ID case is the specific scenario that triggers this bug.
5. **DO NOT** assume that an absent message ID causes a different exception type — it must be specifically `org.apache.camel.processor.idempotent.NoMessageIdException` (which extends `RuntimeCamelException`).