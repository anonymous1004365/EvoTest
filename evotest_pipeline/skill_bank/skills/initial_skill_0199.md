---
name: split-exchange-correlation-id-preservation
description: When splitting an exchange and creating copies, the CORRELATION_ID property
  must be retained on copies. Tests should verify that split copies preserve the original
  correlation ID to prevent downstream routing failures.
code_tags:
- NULL_CHECK
- EDGE_CASE_INPUT
- DATE_PARSE_FORMAT
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# split-exchange-correlation-id-preservation

## Instructions

# Split Exchange Correlation ID Preservation

## Instructions

- WHEN the TG encounters code that copies or splits an Exchange (e.g., `ExchangeHelper.createCopy`, `ExchangeHelper.createCorrelatedCopy`, splitter EIP implementations), and the original exchange has a `CORRELATION_ID` property set via `Exchange.CORRELATION_ID`
- THEN the TG should write a test that:
  1. Creates an exchange and sets `Exchange.CORRELATION_ID` to a specific value
  2. Calls the copy/split method to produce one or more copy exchanges
  3. Asserts that each copy has the same `CORRELATION_ID` property value as the original
  4. If the method under test is expected to generate a *new* correlation ID, the test must assert the old ID is not propagated but a new one is generated instead

- **Common pitfalls to avoid**:
  - Testing only that the exchange body is copied, ignoring the `CORRELATION_ID` property
  - Assuming `Exchange.CORRELATION_ID` is automatically preserved through `Exchange.copy()` without verifying
  - Using `exchange.getExchangeId()` instead of `exchange.getProperty(Exchange.CORRELATION_ID, String.class)` to retrieve the correlation ID
  - Not testing with the exact property key `Exchange.CORRELATION_ID` (whose value is the string `"CamelCorrelationId"`)

- **Correct example** (verifying correlation ID preserved on split copies):
```java
Exchange original = new DefaultExchange(context);
original.setProperty(Exchange.CORRELATION_ID, "myCorrelationId-123");

List<Exchange> copies = splitterStrategy.split(original, body);
for (Exchange copy : copies) {
    String correlationId = copy.getProperty(Exchange.CORRELATION_ID, String.class);
    assertNotNull("CorrelationId should be preserved on split copies", correlationId);
    assertEquals("myCorrelationId-123", correlationId);
}
```

- **Incorrect example** (fails to check CORRELATION_ID property):
```java
Exchange original = new DefaultExchange(context);
original.setProperty(Exchange.CORRELATION_ID, "myCorrelationId-123");

List<Exchange> copies = splitterStrategy.split(original, body);
for (Exchange copy : copies) {
    // BAD: Only checks exchange ID, not CORRELATION_ID property
    assertNotNull(copy.getExchangeId());
    // BAD: Missing assertion on CORRELATION_ID — buggy splitter may drop it
}
```