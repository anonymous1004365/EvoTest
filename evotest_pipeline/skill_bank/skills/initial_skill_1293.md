---
name: template-proxy-type-parameter-validation
description: When testing template substitution visitors that handle type parameters,
  test that both common Java types (String, Integer) AND CtTypeReference instances
  are correctly accepted without throwing ClassCastException. Use this whenever a
  visitor processes heterogeneous parameter collections.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# template-proxy-type-parameter-validation

## Instructions

# Template Proxy Type Parameter Validation

## Instructions

- WHEN the test generator encounters a template substitution visitor (like `SubstitutionVisitor` or `ExtensionDecoupledSubstitutionVisitor`) that processes a map of proxy template parameters where values can be both plain Java types (e.g., `String`, `Integer`) AND Spoon model elements (e.g., `CtTypeReference`),
- THEN the test generator MUST write a test that passes a mixed-type parameter map to ensure no `ClassCastException` is thrown when the visitor iterates over the entries.
  - The test should create a map of proxy parameters containing at least one entry with a `String` value (e.g., `"someString"`) and one entry with a `CtTypeReference` value (e.g., a `CtTypeReference` pointing to `List.class` or any other type).
  - Invoke the visitor's `visit` method (or equivalent entry point) with this map.
  - On the buggy version, the test should throw a `ClassCastException` because the code attempts to cast all parameter values to the same type (e.g., `String`).
  - On the fixed version, the test should pass without exception.
  - Do NOT assume all parameter values are of the same type — proxy template parameters can be heterogeneous.

### Common Pitfalls

- Testing with only one type of parameter value (e.g., all `String`s) — this will NOT trigger the bug.
- Testing with only `CtTypeReference` values — this also may NOT trigger the bug if the code only casts to `CtTypeReference`.
- Assuming the visitor always works with a specific concrete type — the buggy code makes an unsafe assumption about the runtime type of parameter values.

### Example

✅ **Correct test** (catches the bug):
```java
@Test
public void testMixedTypeParametersShouldNotThrow() {
    ExtensionDecoupledSubstitutionVisitor visitor = new ExtensionDecoupledSubstitutionVisitor();
    Map<String, Object> params = new HashMap<>();
    params.put("textParam", "hello");
    params.put("typeParam", factory.Type().get(List.class));
    
    // Should not throw ClassCastException
    visitor.visit(params);
}
```

❌ **Incorrect test** (misses the bug):
```java
@Test
public void testStringParametersOnly() {
    ExtensionDecoupledSubstitutionVisitor visitor = new ExtensionDecoupledSubstitutionVisitor();
    Map<String, Object> params = new HashMap<>();
    params.put("param1", "value1");
    params.put("param2", "value2");
    
    // This passes even on the buggy version!
    visitor.visit(params);
}
```