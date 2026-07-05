---
name: ognl-expression-body-validation
description: When testing OGNL-style simple language expressions with the body() function,
  test that expressions with leading/trailing spaces or mixed content are correctly
  validated and do not cause errors or unexpected behavior.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# ognl-expression-body-validation

## Instructions

# OGNL Expression Body Validation

## Instructions

- WHEN the TG encounters a simple language expression parser that supports OGNL-style syntax (e.g., `${body().OGNL:...}` or `${body(...)}`)
- THEN it should write tests that verify the parser correctly handles edge cases around the `body()` function with OGNL-style parameters, specifically:
  - Leading/trailing spaces in OGNL expressions should NOT cause a `RuntimeBeanExpression` or parsing error
  - The expression `${body().OGNL:...}` should be correctly parsed and evaluated against the message body
  - Mixed content patterns (e.g., `${body().trim()}` combined with `.OGNL:` or other function calls) should all work correctly
- The test should use `ExchangeTestSupport` or similar test base class that provides an `exchange` and `template` for evaluating expressions
- Call `template.evaluate(expression, exchange, String.class)` to evaluate the simple expression
- Verify the result matches the expected transformed value
- **Common pitfall**: Testing only uppercase or perfectly formatted OGNL expressions without testing whitespace edge cases around the `body()` calls
- **Common pitfall**: Assuming that OGNL parameters after `body()` only accept a single type (e.g., only `String`) — test with the actual types used in the codebase (e.g., `String`, `CtTypeReference`)
- **Common pitfall**: Not testing that valid expressions with spaces produce the correct result, not just that they don't throw exceptions

### Correct example:
```java
// Test that OGNL expression with leading/trailing spaces works
public void testBodyOgnlSpaces() throws Exception {
    exchange.getIn().setBody("  Hello World  ");
    template.evaluate("${body().OGNL:trim()}", exchange, String.class);
    assertEquals("Hello World", exchange.getIn().getBody());
}
```

### Incorrect example (missing edge case coverage):
```java
// Only testing non-spaced expressions
public void testBodyOgnl() throws Exception {
    exchange.getIn().setBody("Hello");
    template.evaluate("${body().OGNL:toUpperCase()}", exchange, String.class);
    assertEquals("HELLO", exchange.getIn().getBody());
}
// Missing: test with spaces around body() or in the expression
```