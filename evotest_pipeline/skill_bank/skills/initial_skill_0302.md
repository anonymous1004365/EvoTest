---
name: share-unitOfWork-stopOnException-handled-false
description: WHEN a test exercises a Camel EIP (split, multicast, or recipientList)
  with both shareUnitOfWork() and stopOnException() and an error handler with handled=false,
  THEN the test must verify that a RuntimeException propagates up (i.e., no null exchange
  result) and the route does not silently swallow an exception. This skill prevents
  buggy runtime behavior where exceptions get lost due to interaction between shared
  units of work and stop-on-exception.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# share-unitOfWork-stopOnException-handled-false

## Instructions

# RecipientList/Split/Multicast With Shared UnitOfWork and stopOnException

## Instructions

- **WHEN** the TG encounters a Camel route definition that chains `.shareUnitOfWork().stopOnException()` on a `split()`, `multicast()`, or `recipientList()` EIP — **AND** the route's error handler has `.handled(false)` for the exception clause — **THEN** the TG must write a test that:
  1. Sends a message that will cause an exception in one of the sub-routes (e.g., the first recipient or split element throws an exception).
  2. Calls `template.sendBody("direct:start", <input>)` and stores the result in an `Exchange`.
  3. Asserts that `exchange.getException()` is **not null** and is an instance of a `RuntimeException` (or the specific exception type expected).
  4. Asserts that `exchange.getMessage().getBody()` is **null** (when `handled=false`, the `Exchange` should carry the exception but no normal response body).
- **CRITICAL**: The test must verify that the exception propagates to the caller rather than being silently consumed. Without this skill, the TG might only test the "happy path" where no exception occurs, or might incorrectly assume `handled(false)` always propagates exceptions correctly when combined with `shareUnitOfWork().stopOnException()`.
- **Common pitfall**: Testing `handled(false)` with `stopOnException()` but **without** `shareUnitOfWork()` — that works correctly. The bug only manifests when all three are combined. The TG must ensure the test includes all three: `shareUnitOfWork()`, `stopOnException()`, and `handled(false)`.
- **Common pitfall**: Using `template.requestBody()` instead of `template.send()` — `requestBody` hides exceptions. Use `template.send("direct:start", exchange -> {...})` and then inspect `exchange.getException()` and `exchange.getMessage().getBody()`.
- **Common pitfall**: Assuming the route will throw the exception immediately from `template.sendBody()`. In Camel, `sendBody` might not throw but instead set the exception on the exchange. The test must check `exchange.getException()` after the send completes.

### Correct test example (Java):
```java
@Test
public void testRecipientList() throws Exception {
    Exchange exchange = template.send("direct:start", new Processor() {
        @Override
        public void process(Exchange exchange) throws Exception {
            exchange.getIn().setBody("Hello");
            exchange.getIn().setHeader("foo", "direct:a,direct:b");
        }
    });
    assertNotNull("Should have an exception", exchange.getException());
    assertNull("Body should be null", exchange.getMessage().getBody());
}
```

### Route under test:
```java
from("direct:start")
    .errorHandler(deadLetterChannel("mock:error").maximumRedeliveries(0).redeliveryDelay(0))
    .recipientList(header("foo")).shareUnitOfWork().stopOnException()
    .onException(Exception.class).handled(false).end()
    .to("mock:result");

from("direct:a")
    .throwException(new IllegalArgumentException("Forced error"));
from("direct:b")
    .to("mock:b");
```

### Incorrect test example (would pass on buggy version, fails to detect the bug):
```java
@Test
public void testRecipientList() throws Exception {
    // Only testing normal case, no exception triggered
    template.sendBody("direct:start", "Hello");
    // This would succeed even on buggy version
}
```