---
name: enum-template-parameter-validation
description: When a builder processes template parameters that can be either String
  type names or CtTypeReference types, the test must validate that both input types
  are correctly handled, especially when the parameter represents an enum that also
  has concrete enum constant children.
code_tags:
- BUILDER_PATTERN
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# enum-template-parameter-validation

## Instructions

# Enum Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a builder method (e.g., `addTemplateParameter`, `setTemplateParameter`) that accepts a parameter typed as `Object`, and the implementation inspects the parameter's runtime type to decide whether it's a `String` (class fully-qualified name) or a `CtTypeReference` (already-resolved type reference)
- THEN the TG should write a parameterized test (JUnit `@ParameterizedTest` or equivalent) that passes **both** types of inputs:
  1. A `String` representing the enum type FQN (e.g., `"com.example.MyEnum"`)
  2. A `CtTypeReference` representing the same enum type that was obtained via `factory.Type().get(MyEnum.class)`
  The test must verify that in both cases the builder correctly stores the type reference and that later (e.g., when processing template parameters for enum constant resolution), the code does NOT throw a `ClassNotFoundException`, `NullPointerException`, or produce an incorrect result (e.g., missing enum constants).
- WHEN the template parameter represents an enum class that defines concrete enum constants (e.g., `SINGLE`, `DOUBLE`, `TRIPLE`), the test must also verify that the enum constants are correctly resolved and retrievable from an `EnumAdapter` or similar adapter class, by calling a method like `getEnumValues()` or iterating over `getActualClass().getEnumConstants()`.
- **Common pitfalls:**
  - Testing only one type (e.g., only `String` inputs) — the bug may only occur with `CtTypeReference` inputs because the resolution path differs.
  - Forgetting to check that enum constant children are also correctly handled when the template parameter is a `CtTypeReference` — the class loading may succeed but the enum constants may be lost.
  - Directly comparing type references with `.equals()` without accounting for how the builder wraps/resolves them.
  - Not using `factory.Type().get(...)` to obtain the `CtTypeReference` — use the factory, not manual construction.

### Example: Correct Test Pattern

```java
// Parameterized test with both String and CtTypeReference inputs
@ParameterizedTest
@ValueSource(strings = {"com.example.MyEnum", "CtTypeReference"})
public void testEnumTemplateParameter(String inputType) {
    // arrange
    CtTypeReference<MyEnum> enumRef = factory.Type().get(MyEnum.class);
    Object param = inputType.equals("CtTypeReference") 
        ? enumRef 
        : "com.example.MyEnum";
    
    // act
    builder.addTemplateParameter("MyEnum", param);
    // If builder resolves immediately, expect no exception
    
    // assert: later processing should not throw
    EnumAdapter<?> adapter = ... // get the adapter for the template parameter
    assertNotNull(adapter);
    Object[] enumValues = adapter.getEnumValues();
    assertNotNull(enumValues);
    assertThat(enumValues, arrayContainingInAnyOrder(MyEnum.SINGLE, MyEnum.DOUBLE, MyEnum.TRIPLE));
}
```

### Example: Incorrect Test Pattern (would miss the bug)

```java
// BAD: Only tests String input — misses the bug with CtTypeReference
@Test
public void testEnumTemplateParameter_stringOnly() {
    builder.addTemplateParameter("MyEnum", "com.example.MyEnum");
    // Passes with String, would fail with CtTypeReference
}
```