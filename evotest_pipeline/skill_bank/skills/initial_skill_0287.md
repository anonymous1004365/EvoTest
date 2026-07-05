---
name: variable-access-init-expression-testing
description: When a class has fields with initializer expressions that reference other
  fields or variables, tests must verify that variable references in those initializers
  are correctly typed, including edge cases where implicit type coercion may fail.
  Use this skill for code with CtVariableAccess and implicit type conversion in field
  initialization.
code_tags:
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# variable-access-init-expression-testing

## Instructions

# Variable Access Initialization Expression Testing

## Instructions

- WHEN the TG encounters a class with fields that have initializer expressions (e.g., `int x = something`, `String s = expr`), and the codebase has a CtType system that models these as variable references (CtVariableAccess)
- THEN the TG should write a test that:
  1. Creates a model of a class with at least one field whose initializer references another accessible value (e.g., a method parameter, another field, a literal)
  2. Verifies that each such variable reference in init expressions has a properly resolved `simpleName`, type reference, and that accessing these references does not throw NullPointerException or produce wrong type information
  3. Specifically test edge cases where the init expression involves implicit type conversion (e.g., assigning an `int` literal to a `String` field) — the test must confirm the modeling code handles this gracefully (no exception) and preserves the declared field type correctly
  4. The test should iterate over all field references and assert that each reference's `simpleName` is non-null and that `getType()` returns a non-null type reference
- Common pitfalls to avoid:
  - Testing only a single field type (e.g., only `String` or only `int`) — test at least two different types including one with potential implicit type mismatch
  - Assuming variable accesses always have non-null parent or type — test defensively with assertions for null
  - Forgetting to test the full init expression tree — the test must walk all children of the field's default expression to find variable accesses

### Correct Example (pseudocode)
```java
// Create a class with fields having various init expressions
CtClass<?> cls = factory.createClass("TestClass");
cls.addField(factory.createField().setSimpleName("x").setType(factory.Type().integerPrimitiveType()).setDefaultExpression(factory.createLiteral(42)));
CtField<String> f = cls.addField(factory.createField().setSimpleName("s").setType(factory.Type().stringType()).setDefaultExpression(factory.createLiteral("hello")));

// Access and verify variable references
for (CtField<?> field : cls.getFields()) {
    for (CtVariableAccess va : field.getDefaultExpression().getElements(new TypeFilter<>(CtVariableAccess.class))) {
        assertNotNull(va.getSimpleName(), "VariableAccess name should not be null");
        assertNotNull(va.getType(), "VariableAccess type should not be null");
    }
}
```

### Incorrect Example (pitfall)
```java
// BAD: Only tests one field type, doesn't traverse init expression children
CtField<String> f = ...;
CtVariableAccess va = (CtVariableAccess) f.getDefaultExpression();
assertNotNull(va); // May miss nested accesses or fail with ClassCastException
```