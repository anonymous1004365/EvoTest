---
name: lambda-type-parameter-getdeclaration
description: When a lambda expression has type parameters that reference external
  types, getDeclaration() may return null on the type parameter's type. This skill
  teaches how to test for proper null handling of getDeclaration() results on type
  parameters from lambda expressions.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# lambda-type-parameter-getdeclaration

## Instructions

# Lambda Type Parameter getDeclaration() Null Safety

## Instructions

WHEN testing a method that calls `getDeclaration()` on a `CtTypeReference` obtained from a type parameter in a lambda expression (e.g., a lambda with explicit type parameters like `(String s, List<String> list) -> ...`):

- THEN the test MUST verify that calling `getDeclaration()` on the type reference of the lambda's type parameter does NOT throw a `NullPointerException` or `ClassNotFoundException`.

- WHEN the lambda's type parameter references a type that is not a declared class but a type variable or parameterized type (e.g., `T` in `<T>`, or `List<String>` where `String` appears in a type argument position within a lambda parameter):

- THEN the test MUST call `getDeclaration()` on the `CtTypeReference` of each type parameter and assert that the result is either non-null OR that the call completes without exception — specifically, on the buggy version this call throws an exception.

- When iterating over a lambda's parameters (via `getParameters()`) and obtaining their types (via `getType()`), the test MUST call `getDeclaration()` on each type reference and should expect either:
  - A valid `CtType` declaration for standard Java types (like `java.lang.String`), OR
  - A safe null/exception-free return for type variables or parameterized types in lambda contexts.

- Common pitfalls:
  - ❌ ONLY testing `getDeclaration()` on simple named types without lambda context.
  - ❌ Assuming all type references from lambda parameters have declarations.
  - ❌ Not testing the specific lambda+type-parameter scenario where the bug manifests.

## Correct Example (simplified)

```java
// Given a lambda parameter with a type argument like:
//   (List<String> list) -> { ... }
// Iterate over lambda parameters and call getDeclaration() on each type reference:

CtExecutableReference<?> ref = lambda.getExecutableReference();
if (ref != null) {
    for (CtParameter<?> param : ref.getParameters()) {
        CtTypeReference<?> paramType = param.getType();
        for (CtTypeReference<?> typeArg : paramType.getActualTypeArguments()) {
            // Should not throw NullPointerException or ClassNotFoundException
            CtType<?> declaration = typeArg.getDeclaration();
            // declaration may be null for some types (e.g. type variables),
            // but the call itself should not fail
        }
    }
}
```

## Incorrect Example

```java
// ❌ This only tests simple cases and misses the lambda context bug:
CtTypeReference<?> ref = factory.Type().get(String.class);
CtType<?> decl = ref.getDeclaration();  // Works fine, misses the bug

// ❌ This assumes getDeclaration() always succeeds:
for (CtTypeReference<?> typeArg : paramType.getActualTypeArguments()) {
    CtType<?> decl = typeArg.getDeclaration();  // Might throw on buggy version!
    decl.getSimpleName();  // NPE on buggy version if getDeclaration() threw
}
```