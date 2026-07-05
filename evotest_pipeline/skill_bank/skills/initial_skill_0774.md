---
name: ognl-method-ambiguity-on-overloaded-methods
description: WHEN the TG sees OGNL method chains on Java standard library types (like
  String, Integer, etc.) that have overloaded methods with different parameter types
  (e.g., toUpperCase(Locale) vs toUpperCase()), THEN test that the OGNL expression
  resolves without AmbigiousMethodCallException. Includes testing with both no-arg
  and Locale-arg variants of methods.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- OGNL_METHOD_AMBIGUITY
- BEAN_PROPERTY_ASSIGNMENT
- TYPE_CONVERSION
test_pattern: INTERACTION_TEST
---

# ognl-method-ambiguity-on-overloaded-methods

## Instructions

# OGNL Method Ambiguity on Overloaded Methods

## Instructions

- WHEN the TG encounters a `BeanExpression` or `SimpleLanguage` that processes OGNL method chains (e.g., `${body.toUpperCase()}`) AND the method being invoked is **overloaded** (has multiple variants with different parameter types in the JDK or library class), THEN the TG should write a test that verifies OGNL resolution does NOT throw `AmbiguousMethodCallException`.

- Specifically, WHEN the method is `String.toUpperCase()` (which has two overloads: `toUpperCase()` and `toUpperCase(Locale)`), THEN the TG should:
  1. Create a route using simple language expression `${body.toUpperCase()}`.
  2. Send a `String` message body, e.g., `"Camel"`.
  3. Assert that the result equals the body converted to uppercase (e.g., `"CAMEL"`).
  4. Assert that no `AmbiguousMethodCallException` is thrown during evaluation (the method should resolve to the no-arg variant).

- WHEN the TG encounters any OGNL method on a type where the method name has multiple overloads differing only by **argument types** (not count), THEN the TG should test that the expression resolves correctly, because the OGNL introspection may fail to pick the best match and throw an ambiguous error.

- The TG should include test cases that compare:
  - The OGNL expression `${body.toUpperCase()}` against a known expected value.
  - The OGNL expression `${body.toUpperCase(java.util.Locale.ENGLISH)}` against a known expected value.
  - Both should succeed without ambiguity errors on the **fixed** version.

- Common pitfalls:
  - Testing only with custom POJO methods (which are less likely to have ambiguous overloads). The bug specifically affects JDK types like `String`, `Integer`, etc.
  - Forgetting to check that an expression with the method name only (no arguments) succeeds. The ambiguity only manifests when the method has no explicit arguments in the OGNL expression but has multiple overloads in the class.
  - Using MOCK tests that bypass the actual `BeanExpression` or `SimpleLanguage` evaluation — the TG must use an integration-style test with a real Camel route.

### Example (Correct)

```java
public void testBodyOgnlOnString() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .transform().simple("${body.toUpperCase()}")
                .to("mock:result");
        }
    });
    
    context.start();
    template.sendBody("direct:start", "Camel");
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedBodiesReceived("CAMEL");
    mock.assertIsSatisfied();
}
```

### Example (Incorrect — wouldn't catch the bug)

```java
public void testBodyOgnlOnCustomPojo() throws Exception {
    // This uses a custom class where the method is not overloaded
    // It wouldn't catch the String.toUpperCase() ambiguity bug
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .transform().simple("${body.getName()}")
                .to("mock:result");
        }
    });
    // ...
}
```