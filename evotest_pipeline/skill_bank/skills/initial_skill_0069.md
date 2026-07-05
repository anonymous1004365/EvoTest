---
name: wildcard-type-substitution-validation
description: Validates that wildcard types with upper bounds (e.g., `? extends T`)
  are correctly substituted when creating generic method references. When a method
  reference includes captured wildcards as type arguments, the substitution must preserve
  the correct type rather than incorrectly using the raw wildcard upper bound.
code_tags:
- GENERIC_METHOD_REFERENCE
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# wildcard-type-substitution-validation

## Instructions

# Wildcard Type Substitution in Generic Method References

## Instructions

- WHEN the TG encounters code that creates method references to generic methods where one or more type arguments involve captured wildcards with upper bounds (e.g., `? extends T`), or any code that substitutes type variables with actual types in a method reference (particularly in a code generation/transformation framework like Spoon)
- THEN the TG should write a test that:
  1. Creates a scenario where a method reference targets a generic method
  2. The type arguments of the method reference involve a wildcard with an upper bound (e.g., `? extends String`), NOT just a concrete type like `String` or `CtTypeReference<String>`
  3. Verifies that after type substitution, the resulting method reference correctly preserves the wildcard upper bound type rather than replacing it with a different type (like `Object`)
  4. Specifically, for Spoon-like frameworks, the test should verify that when creating a method reference like `List::addAll` with a type argument of `? extends T`, the actual type parameter used is the wildcard's bound (e.g., `String`), not `Object`
  5. Expect that on the buggy version, the type argument incorrectly becomes `Object` instead of the correct upper bound type, causing the test to fail or produce wrong results

- Common pitfalls to avoid:
  - **Testing only concrete types**: Writing tests that use concrete type arguments (e.g., `String`, `Integer`) will NOT catch this bug. The TG must test with wildcard-bounded types specifically.
  - **Testing only single-type references**: The TG might test method references with one type parameter, but the bug may only manifest with multiple type parameters or specific wildcard patterns.
  - **Assuming type inference works**: Do NOT assume the framework correctly infers wildcard bounds. The test must explicitly create a type reference involving `? extends X` and verify the substitution result.
  - **Forgetting to compare against the expected bound type**: The test must compare the substituted type against the wildcard's upper bound (e.g., `String`), not just check that it's non-null.

### Example (Correct Test Approach):
```java
// Create a wildcard type: ? extends String
CtTypeReference<?> stringTypeRef = factory.Type().stringType();
CtTypeReference<?> wildcardType = factory.Type().createWildcardReference(stringTypeRef);

// Create a method reference to a generic method like List::addAll(Collection<? extends E>)
// where the type argument is the wildcard
CtMethodReference<?> methodRef = ...; 
methodRef.setTypeArguments(Collections.singletonList(wildcardType));

// Perform substitution
CtMethodReference<?> substituted = methodRef.substitute(...);

// VERIFY: the type argument should be String (the upper bound), NOT Object
assertEquals("String", substituted.getTypeArguments().get(0).getQualifiedName());
```

### Example (Incorrect Test — Would Miss the Bug):
```java
// Only testing with a concrete type — won't trigger the wildcard path
CtTypeReference<String> stringTypeRef = factory.Type().stringType();
CtMethodReference<?> methodRef = ...;
methodRef.setTypeArguments(Collections.singletonList(stringTypeRef));

// This test passes even on the buggy version because concrete types are handled correctly
CtMethodReference<?> substituted = methodRef.substitute(...);
assertEquals("String", substituted.getTypeArguments().get(0).getQualifiedName());
```