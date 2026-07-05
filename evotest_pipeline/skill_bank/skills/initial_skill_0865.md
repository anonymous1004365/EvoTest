---
name: parameter-modifier-validation
description: When building Java source code via JavaPoet's ParameterSpec, modifiers
  are validated per Java language rules. This skill helps test generators write tests
  that ensure parameter modifier validation rejects illegal modifier combinations.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# parameter-modifier-validation

## Instructions

# Parameter Modifier Validation

## Instructions

- WHEN the TG encounters code that calls `ParameterSpec.builder()` with modifiers (e.g., `Modifier.FINAL`, `Modifier.PRIVATE`, `Modifier.STATIC`, `Modifier.VOLATILE`, `Modifier.TRANSIENT`)
- THEN the test should verify that adding **non-allowed modifiers** (such as `FINAL`) to a parameter throws an `IllegalArgumentException`
- Specifically, test that `ParameterSpec.builder(TypeName typeName, String name, Modifier... modifiers)` rejects the `Modifier.FINAL` modifier (and potentially other illegal modifiers like `VOLATILE`, `TRANSIENT`, `STATIC`, `PRIVATE`) with an appropriate exception
- The test should call `ParameterSpec.builder(Types.INT, "foo", Modifier.FINAL).build()` and expect `IllegalArgumentException` to be thrown
- Common pitfall: Testing only that valid modifiers (like `PUBLIC` or nothing) work, without verifying rejection of invalid modifiers like `FINAL`
- Common pitfall: Assuming all Java modifiers are valid for method parameters — parameters cannot be `final`, `volatile`, `transient`, or have access modifiers like `private`/`public`

### Correct example:
```java
@Test(expected = IllegalArgumentException.class)
public void addNonFinalModifier() {
  ParameterSpec.builder(Types.INT, "foo", Modifier.FINAL).build();
}
```

### Incorrect approach (would miss the bug):
```java
// This only tests valid modifiers — does NOT catch the validation bug
@Test
public void addPublicModifier() {
  ParameterSpec spec = ParameterSpec.builder(Types.INT, "foo", Modifier.PUBLIC).build();
  assertEquals("int foo", spec.toString());
}
```