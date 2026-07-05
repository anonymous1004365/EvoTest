---
name: proxy-custom-processor-predicate-evaluation
description: When a proxy method that wraps custom processor instances is used to
  create a predicate-based route, the TG must test with processor instances that are
  not of type String to ensure evaluateAsPredicate does not throw ClassCastException.
  This skill applies to ProxyHelper and similar proxy-creation utility methods.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# proxy-custom-processor-predicate-evaluation

## Instructions

# Proxy Custom Processor Predicate Evaluation

## Instructions

- WHEN the code under test uses `ProxyHelper.createProxy()` or similar dynamic proxy creation to wrap custom processor instances into a route/endpoint, and the route uses a predicate-based expression (e.g., the `evaluateAsPredicate` method in `ObjectHelper`)
- THEN the TG must write a test that verifies that when a custom processor whose `process(Exchange)` method calls `exchange.getIn().setBody(...)` with a non-String object type (e.g., an `Integer` or a domain object), the predicate evaluation does **not** throw a `ClassCastException` caused by incorrectly casting the custom processor's result to `String`
- The test should specifically use a concrete processor implementation (not an anonymous inline lambda) that sets the exchange body to a non-String object like `Integer.valueOf(123)`, then evaluate the body as a predicate (e.g., `ObjectHelper.evaluateAsPredicate(exchange)`), and assert that it returns the expected boolean result without throwing an exception
- Common pitfalls to avoid:
  - Testing only with `String`-typed body values, which hides the casting bug
  - Forgetting to create a full `Exchange` with proper `In` message and body before calling the predicate evaluation method
  - Assuming that custom processor results are always `String` when returned through the proxy chain
  - Not including the proxy creation step that wraps the processor before predicate evaluation

**Correct example (should pass on fixed code):**
```java
@Test
public void testEvaluateAsPredicateWithNonStringBody() {
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setBody(Integer.valueOf(123));
    assertTrue(ObjectHelper.evaluateAsPredicate(exchange));
}

@Test
public void testEvaluateAsPredicateWithNullBody() {
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setBody(null);
    assertFalse(ObjectHelper.evaluateAsPredicate(exchange));
}
```

**Incorrect example (hides the bug):**
```java
@Test
public void testEvaluateAsPredicateOnlyWithString() {
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setBody("Hello");
    assertTrue(ObjectHelper.evaluateAsPredicate(exchange));
    // Does NOT test with Integer, null, or other non-String types
}
```