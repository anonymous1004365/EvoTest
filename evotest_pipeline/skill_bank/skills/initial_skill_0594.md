---
name: multi-parameter-lambda-type-reference-access
description: When a lambda expression has multiple parameters, accessing the type
  reference (getType()) of one parameter may return a type that shadows another parameter's
  type instead of its own. Use this skill to write tests that verify each parameter's
  type reference is correctly resolved.
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# multi-parameter-lambda-type-reference-access

## Instructions

# Multi-Parameter Lambda Type Reference Validation

## Instructions

- WHEN the TG encounters code that accesses the type of an individual parameter in a multi-parameter lambda expression (e.g., `lambda.getParameters().get(i).getType()`), and when the lambda's body references another parameter before referencing the one being queried
- THEN the TG should write a parametric test that:
  1. Creates a multi-parameter lambda (at least 2 parameters, e.g., `(a, b) -> someExpressionUsingA` or using both)
  2. Retrieves each parameter's type reference via `lambda.getParameters().get(i).getType()`
  3. Verifies that each parameter's type is valid (non-null) and correctly corresponds to the parameter, not shadowing another parameter's type
  4. Specifically for the buggy version, assert that `parameter.getType()` returns a non-null type reference (e.g., `CtTypeReference`) that correctly identifies the parameter's own inferred type — not the type of a sibling parameter
- Common pitfalls:
  - Testing only single-parameter lambdas, which do not trigger the shadowing bug
  - Testing only the first parameter's type in a multi-parameter lambda, while the bug affects later parameters when earlier parameters are referenced in the lambda body
  - Assuming that if `getType()` returns non-null, it is correct — the bug returns a wrong type reference (shadowing), not null
- Example of a correct test:
```java
@Test
public void testMultiParameterLambdaTypeReference() {
    CtModel model = launcher.getModel();
    CtType<?> type = model.getType("some.package.SomeType");
    CtLambda<?> lambda = type.getMethodsByName("methodReturningFunctionalInterface").get(0).getBody().getStatement(0);
    // lambda like (x, y) -> x.something()
    // Verify that parameter 0 has a non-null type reference for x
    assertNotNull(lambda.getParameters().get(0).getType());
    // Verify that parameter 1 has a non-null type reference for y (not shadowing x's type)
    assertNotNull(lambda.getParameters().get(1).getType());
}
```
- Example of an incorrect test (does not catch the bug):
```java
@Test
public void testSingleParameterLambda() {
    // Single-parameter lambda does not trigger the shadowing bug
    CtLambda<?> lambda = ...; // (x) -> x.doSomething()
    assertNotNull(lambda.getParameters().get(0).getType()); // passes even on buggy
}
```