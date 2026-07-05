---
name: bean-binding-type-check-on-parameterized-class
description: When a Camel route binds to a bean that extends a parameterized superclass
  (e.g., AbstractTransformer<String>), the test must verify type-safe method dispatch
  works correctly. This skill helps test that Camel properly resolves method parameters
  by their generic type rather than falling back to Object when the declaring class
  is generic and the subclass extends it with a concrete type argument.
code_tags:
- TYPE_CONVERSION
- ARGUMENT_VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# bean-binding-type-check-on-parameterized-class

## Instructions

# Bean Binding Type Check on Parameterized Class

## Instructions

- WHEN the TG encounters a Camel route that uses `.bean(SomeImpl.class, "methodName")` where `SomeImpl` extends a **parameterized superclass** (e.g., `AbstractTransformer<String>`) and the superclass has a method with a **parameterized-type parameter** (e.g., `T body` in `AbstractTransformer<T>`), and the superclass also has a separate **overloaded method** that takes `Object` — THEN the TG should write a test that sends a message with a body of the **concrete type argument** (e.g., `String` body) and verifies the **correct specific method** is invoked (the one with the concrete parameter type, not the `Object` fallback).

- The key risk is that Camel's `BeanInfo` may resolve method parameter types based on the **declaring class** rather than the **runtime class** of the bean. When `AbstractTransformer<String>` declares `public void transform(T body)` and `public void transform(Object body)`, the generic method `transform(T body)` on the **declaring class** `AbstractTransformer` has `T` erased to `Object`. This can cause `BeanInfo` to incorrectly match both methods as `transform(Object)` and pick the wrong one (e.g., the `Object` method), resulting in a `ClassCastException` or `CamelExecutionException` at runtime.

- WHEN testing this scenario, the TG MUST verify that after the route processes a message with a body of the concrete type (e.g., `String`), the **subclass's overridden method** with the **concrete parameter type** (e.g., `TransformerImpl.transform(String body)`) was invoked, not the `Object` overload on the superclass. The test should assert the **expected transformed output** (e.g., `"Hello World"` → `"Transformed: Hello World"`).

- Common pitfalls to avoid:
  - **Testing only with `Object` type parameters**: Sending an `Object` body won't trigger the bug because both methods accept `Object` — use the **specific concrete type** (e.g., `String`).
  - **Assuming `T` is always resolved correctly**: Just because `TransformerImpl` extends `AbstractTransformer<String>`, don't assume Camel will resolve `T` to `String` during method matching. The generic type variable `T` on the **declaring class** may still be treated as `Object` by BeanInfo's introspection.
  - **Writing tests that pass even on the buggy version**: A test that doesn't trigger method dispatch ambiguity will pass regardless of the bug. Ensure the test body type forces the ambiguous resolution path.
  - **Not checking the output/behavior**: Instead of just asserting no exception, verify the **transformed result** is correct to ensure the right method ran.

### Example (correct approach):

```java
// Route under test
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("direct:start")
            .bean(TransformerImpl.class, "transform");
    }
});

// Test
@Test
public void testTransformer() {
    String result = template.requestBody("direct:start", "Hello World", String.class);
    // The buggy version would invoke AbstractTransformer.transform(Object body)
    // which returns "Hello World" unchanged (a no-op).
    // The fixed version invokes TransformerImpl.transform(String body)
    // which returns "Transformed: Hello World".
    assertEquals("Transformed: Hello World", result);
}
```

### Example (incorrect approach):

```java
// WRONG: Sending an Object body won't differentiate between the two methods
@Test
public void testTransformerWrong() {
    Object result = template.requestBody("direct:start", new Object(), Object.class);
    // Both methods accept Object, so this test passes even on buggy code.
    // It does NOT exercise the type resolution bug.
    assertNotNull(result);
}
```