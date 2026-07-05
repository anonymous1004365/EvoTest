---
name: bean-handler-predicate-return-value
description: When a bean implements Predicate interface and is used in a Camel route,
  its evaluate() method may be triggered instead of the intended handler method, returning
  a boolean instead of the expected result. This skill teaches how to test that the
  correct handler method is invoked rather than the Predicate.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: STATE_TEST
---

# bean-handler-predicate-return-value

## Instructions

# Bean Handler Predicate Return Value

## Instructions

**WHEN** the TG encounters a Camel bean class that implements the `Predicate` interface (i.e., `org.apache.camel.Predicate` with an `evaluate(Exchange)` method) AND is used as a bean in a `bean:` or `.bean()` route with a specific handler method (e.g., `.bean(MyHandlerPredicateBean.class, "handleMethod")`):

- **THEN** the TG should verify that the bean's handler method is actually invoked and its return value reaches the route output, rather than the bean's `evaluate(Exchange)` method (inherited from `Predicate`) being silently invoked and returning a `boolean`.

- **Specifically**, test that the handler method's return value is preserved in the exchange body by calling the handler method on the bean directly and asserting the result equals the expected value. For example, if `MyHandlerPredicateBean.handleMethod(String body)` returns `"Hi " + body`, then `bean.handleMethod("Camel")` should return `"Hi Camel"`.

- **Also**, the TG should write an integration test using Camel's `ProducerTemplate` to send a message through the route and verify the output body equals the expected handler return value (e.g., `"Hi Camel"`), NOT a boolean like `"true"` or `"false"`.

- **Common pitfalls to avoid:**
  - ❌ Testing only that the route runs without exception — this would pass even if the wrong method (evaluate) is called.
  - ❌ Assuming the handler method will be correctly resolved when the bean also implements `Predicate` — the bug occurs because the Camel bean component may incorrectly choose the `evaluate` method over the named handler method.
  - ❌ Checking only that the body is non-null or that some mock endpoint is reached — the test must assert the *exact string value* that the handler method returns.

**Correct example:**

```java
// Direct unit test of the handler method
MyHandlerPredicateBean bean = new MyHandlerPredicateBean();
String result = bean.handleMethod("Camel");
assertEquals("Hi Camel", result);

// Integration test via Camel route
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() {
        from("direct:start")
            .bean(MyHandlerPredicateBean.class, "handleMethod")
            .to("mock:result");
    }
});
String result = template.requestBody("direct:start", "Camel", String.class);
assertEquals("Hi Camel", result);
mockResult.expectedBodiesReceived("Hi Camel");
mockResult.assertIsSatisfied();
```

**Incorrect example:**

```java
// ❌ This test would PASS on the buggy code because it doesn't check the body value
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() {
        from("direct:start")
            .bean(MyHandlerPredicateBean.class, "handleMethod")
            .to("mock:result");
    }
});
template.sendBody("direct:start", "Camel");
mockResult.expectedMessageCount(1);
mockResult.assertIsSatisfied(); // This passes even when body is "true" instead of "Hi Camel"
```

**When the bean implements `Predicate` and a handler method is explicitly specified (e.g., `"handleMethod"`), always assert the exact return value string to ensure the correct method is being dispatched, not the inherited `evaluate()` method.**