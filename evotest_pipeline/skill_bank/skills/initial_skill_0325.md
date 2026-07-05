---
name: annotation-expression-return-type-predicate
description: When an annotation-based expression factory creates an Expression for
  a parameter whose return type is Boolean or boolean, the factory should create a
  Predicate instead of an Expression. Test both parameter types (String vs boolean/Boolean)
  for annotation injection beans to catch incorrect Expression vs Predicate creation.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
- ANNOTATION_PRESENCE_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# annotation-expression-return-type-predicate

## Instructions

# Annotation Expression Return Type Predicate Handling

## Instructions

- WHEN the TG encounters a bean method parameter annotated with a language annotation (e.g., `@Simple`, `@XPath`, `@Bean`) whose parameter type is `boolean` or `Boolean`, and the annotation expression factory creates an `Expression` via `language.createExpression(expression)`
- THEN the TG should write a test that verifies the behavior when the parameter type is `boolean.class` or `Boolean.class` — specifically, the TG must verify that the factory creates a `Predicate` and returns it wrapped in a `PredicateToExpressionAdapter` (so the expression evaluates to `true` or `false` depending on whether the predicate matches), NOT a plain `Expression` that evaluates the expression as a value-producing expression
- The TG should test with both a `String` parameter type (where expression evaluation applies) and a `boolean`/`Boolean` parameter type (where predicate evaluation applies), using a bean that receives a method parameter annotated with e.g. `@Simple("${header.foo} != null") boolean foo`
- The TG should verify that when the header exists, the boolean parameter is `true`, and when the header is absent, the boolean parameter is `false`
- Common pitfalls to avoid:
  - Testing only with `String` parameter types and assuming all expression evaluation works identically for boolean parameters
  - Not checking that a `PredicateToExpressionAdapter` is used to wrap the predicate into an expression
  - Assuming `language.createPredicate()` is called instead of verifying through the behavior (the evaluation result)
  - Writing tests that only check for exceptions rather than both positive and negative cases

### Correct test example:
```java
// Test with boolean parameter type annotated with @Simple
// This verifies that the expression return type causes a Predicate to be created
// and then adapted into an Expression

// Route: from("direct:in").beanRef("myBean");
public static class MyBean {
    public String body;
    public boolean foo;
    public void read(String body, @Simple("${header.foo} != null") boolean foo) {
        this.body = body;
        this.foo = foo;
    }
}

// Test 1: header is present → predicate matches → foo=true
public void testSendMessageWithFoo() throws Exception {
    template.sendBodyAndHeader("direct:in", "Hello", "foo", 123);
    assertEquals("Hello", myBean.body);
    assertEquals(true, myBean.foo);
}

// Test 2: header is absent → predicate does NOT match → foo=false
public void testSendMessageWithoutFoo() throws Exception {
    template.sendBody("direct:in", "Hello");
    assertEquals("Hello", myBean.body);
    assertEquals(false, myBean.foo);
}
```

### Incorrect test example:
```java
// Only testing the String case — misses the bug entirely
public void testSendMessage() throws Exception {
    template.sendBody("direct:in", "Hello");
    assertEquals("Hello", myBean.body);
    // Never tests boolean annotation parameter type
}

// Or: Testing only that no exception is thrown, not the actual boolean value
public void testNoException() throws Exception {
    template.sendBodyAndHeader("direct:in", "Hello", "foo", 123);
    // Missing assertion on the boolean value
}
```