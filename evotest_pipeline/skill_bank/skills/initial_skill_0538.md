---
name: invalid-ognl-bracket-syntax-detection
description: WHEN the TG encounters bean language OGNL method expressions (e.g., "getOther[xx"),
  THEN it should test that invalid bracket syntax is detected and throws ExpressionIllegalSyntaxException.
  This helps catch missing validation for unpaired square brackets in OGNL expressions.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
- INPUT_VALIDATION
- SYNTAX_VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# invalid-ognl-bracket-syntax-detection

## Instructions

# Invalid OGNL Bracket Syntax Detection

## Instructions

- WHEN the TG encounters code that validates OGNL expressions (methods like `isInvalidValidOgnlExpression`, `isValidOgnlExpression`, or methods that call `OgnlHelper` such as `BeanExpression.evaluate()`), and the validation checks for bracket pairing using `StringHelper.countChar`
- THEN the TG should write a test that uses a bean expression method string containing an **unpaired opening bracket** `[` without a corresponding closing bracket `]`, such as `"getOther[xx"` or `"someMethod[abc"`, and verify that:
  1. The expression throws `RuntimeBeanExpressionException` (wrapping an `ExpressionIllegalSyntaxException`)
  2. The `ExpressionIllegalSyntaxException` has `getExpression()` equal to the invalid method string and `getMessage()` containing `"Illegal syntax: "`
  3. The exception chain includes `MethodNotFoundException` with `getMethodName()` equal to the invalid method string
- The test must use `FailedToCreateRouteException` when testing at route creation time (via `context.start()`), or can test directly on `BeanExpression.evaluate()` with a mock `Exchange`
- Common pitfalls to avoid:
  - Testing only valid OGNL expressions (e.g., `getOther["key"]`) and not testing invalid bracket syntax
  - Testing with only balanced brackets like `"getOther[xx]"` — the bug is specifically about **unpaired** brackets
  - Assuming the test must use real bean instances in a full Camel route — testing the validation at route creation time works, or using a direct `BeanExpression` + mock exchange approach

**Correct example (test with invalid OGNL at route creation time):**

```java
public void testInvalidOgnlBracketSyntax() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .transform().method(MyBean.class, "getOther[xx");
        }
    });
    try {
        context.start();
        fail("Should have thrown exception");
    } catch (FailedToCreateRouteException e) {
        RuntimeCamelException rce = assertIsInstanceOf(RuntimeCamelException.class, e.getCause());
        MethodNotFoundException mnfe = assertIsInstanceOf(MethodNotFoundException.class, rce.getCause());
        assertEquals("getOther[xx", mnfe.getMethodName());
        ExpressionIllegalSyntaxException cause = assertIsInstanceOf(ExpressionIllegalSyntaxException.class, mnfe.getCause());
        assertEquals("Illegal syntax: getOther[xx", cause.getMessage());
        assertEquals("getOther[xx", cause.getExpression());
    }
}
```

**Incorrect example (missing the unpaired bracket scenario):**

```java
// BAD: Only tests valid expressions
public void testValidOgnl() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .transform().method(MyBean.class, "getOther"); // valid, no brackets
        }
    });
    context.start(); // passes but doesn't test the bug
}
```