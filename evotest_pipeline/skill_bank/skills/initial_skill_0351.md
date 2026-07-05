---
name: pojo-field-type-mismatch-validation
description: When creating PojoField with getter/setter type mismatches, test that
  the PojoField rejects incompatible getter-return and setter-parameter types by throwing
  an exception. This skill is applicable when constructing PojoTypeInfo from classes
  where field accessor types (getter return type vs setter parameter type) may differ.
code_tags:
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# pojo-field-type-mismatch-validation

## Instructions

# PojoField Getter/Setter Type Mismatch Validation

## Instructions

WHEN the TG encounters code that constructs a `PojoField` or `PojoTypeInfo` where a POJO class has getter and setter methods with mismatching types (e.g., getter returns `Integer` but setter accepts `int`, or vice versa), THEN the TG should write a test that:

1. Defines a POJO class with a property where the getter return type differs from the setter parameter type (e.g., getter returns `Integer` (boxed) while setter takes `int` (primitive), or getter returns `Long` while setter takes `String`).
2. Calls `TypeExtractor.getForClass(YourPojo.class)` to create the `PojoTypeInfo`.
3. Expects that constructing the `PojoTypeInfo` throws an appropriate exception (e.g., `IllegalArgumentException`, `RuntimeException`, or another exception indicating type incompatibility).

Specifically:
- The test should verify that when the getter and setter for the same field have Java type mismatches (e.g., `Integer` vs `int`), the `PojoTypeInfo` construction does NOT silently succeed. It must throw an exception to prevent downstream ClassCastExceptions during serialization/deserialization.
- Use `Assert.assertThrows` or a `@Test(expected = ...)` annotation to assert the expected exception.
- The exception message should indicate that the types are incompatible (e.g., contain "does not match" or "incompatible").

Common pitfalls to avoid:
- Testing only with perfectly matching getter/setter types (e.g., both `Integer` and `Integer`). You must test the **mismatched** case.
- Overlooking primitive-to-boxed type mismatches like `int` ↔ `Integer` – these are also type mismatches that should be caught.
- Assuming `PojoField` handles type coercion/conversion automatically — it does not.
- Testing only the `PojoField` constructor directly without going through `PojoTypeInfo` or `TypeExtractor`.

### Correct Example (what the test should look like)

```java
// POJO with getter returning Integer, setter taking int
public static class MismatchedGetterReturnType {
    private Integer value;

    public Integer getValue() { return value; }
    public void setValue(int value) { this.value = value; }
}

@Test(expected = IllegalArgumentException.class)
public void testPrimitivePojoGetterReturnTypeMismatch() {
    PojoTypeInfo<?> typeInfo = (PojoTypeInfo<?>) TypeExtractor.getForClass(MismatchedGetterReturnType.class);
    // Should throw IllegalArgumentException because getter returns Integer but setter takes int
}
```

OR using Assert.assertThrows:

```java
@Test
public void testPrimitivePojoGetterReturnTypeMismatch() {
    assertThrows(IllegalArgumentException.class, () -> {
        TypeExtractor.getForClass(MismatchedGetterReturnType.class);
    });
}
```

### Incorrect Example (what the test should NOT look like)

```java
// BAD: Only tests with matching types
public static class GoodPojo {
    private Integer value;
    public Integer getValue() { return value; }
    public void setValue(Integer value) { this.value = value; }
}

@Test
public void testGoodPojo() {
    // This passes always - doesn't test the buggy scenario
    PojoTypeInfo<?> typeInfo = (PojoTypeInfo<?>) TypeExtractor.getForClass(GoodPojo.class);
    assertNotNull(typeInfo);
}
```

The incorrect example only tests the happy path and would never catch the bug where mismatched getter/setter types cause the `PojoField` to silently accept incompatible types.