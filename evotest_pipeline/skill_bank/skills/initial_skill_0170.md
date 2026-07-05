---
name: send-dynamic-exchange-pattern
description: When using SendDynamicProcessor with the exchangePattern option, the
  exchange's MEP (Message Exchange Pattern) gets overwritten to InOut after sending
  to the dynamic endpoint. Teach the TG to verify that exchange pattern options are
  correctly preserved on the outgoing exchange, not just the incoming endpoint URI.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# send-dynamic-exchange-pattern

## Instructions

# SendDynamic Exchange Pattern Option Preservation

## Instructions

- WHEN the TG encounters a route using `.toD()` (SendDynamicProcessor) with an `exchangePattern` option (e.g., `InOnly` or `InOut`) on a `from()` or `.to()` endpoint
- THEN the TG should write a test that verifies the exchange pattern on messages **received at downstream mock endpoints** (not just on the initial exchange), specifically checking that:
  - A mock endpoint receiving the exchange after `.toD()` has the correct `exchangePattern` as set by the option
  - For `exchangePattern=InOnly`, assert: `getMockEndpoint("mock:result").message(0).exchangePattern().isEqualTo(ExchangePattern.InOnly)`
  - For `exchangePattern=InOut`, assert: `getMockEndpoint("mock:result").message(0).exchangePattern().isEqualTo(ExchangePattern.InOut)`
- WHEN testing `SendDynamicProcessor` or `.toD()` with exchange pattern options
- THEN the TG must also create a separate test method **per exchange pattern value** (`testExchangePatternOptionInOnly`, `testExchangePatternOptionInOut`) because each pattern is independently bug-prone
- Common pitfalls:
  - ❌ Testing only the incoming exchange pattern before the send — the bug happens when the exchange pattern gets overwritten **during** the send to the dynamic endpoint
  - ❌ Testing only one exchange pattern (e.g., only `InOnly`) — the fix may work for one but not the other
  - ❌ Using `.to()` directly instead of `.toD()` — `.toD()` uses `SendDynamicProcessor` which has the bug; `.to()` uses `SendProcessor` which may not

### Correct test pattern:

```java
@Test
public void testExchangePatternOptionInOut() throws Exception {
    getMockEndpoint("mock:result").expectedMessageCount(1);
    getMockEndpoint("mock:stub").expectedMessageCount(1);
    getMockEndpoint("mock:result").message(0).exchangePattern().isEqualTo(ExchangePattern.InOut);
    getMockEndpoint("mock:stub").message(0).exchangePattern().isEqualTo(ExchangePattern.InOut);

    template.sendBody("direct:startInOut", "Hello World");

    assertMockEndpointsSatisfied();
}
```

### Incorrect test pattern (misses the bug):

```java
@Test
public void testExchangePatternOptionInOut() throws Exception {
    // ❌ Only checks initial exchange, not the mock endpoints after delivery
    Exchange exchange = template.send("direct:startInOut", e -> e.getIn().setBody("Hello World"));
    assertEquals(ExchangePattern.InOut, exchange.getPattern());
}
```