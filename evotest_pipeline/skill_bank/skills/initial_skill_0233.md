---
name: nested-pojo-type-key-validation
description: When testing key expression selection on nested POJO fields within tuples,
  verify that type validation correctly rejects incompatible field types (e.g., using
  a POJO field inside a tuple as a grouping key when the field type is a non-comparable
  type like Tuple2). Helps detect cases where type validation logic misses checking
  the inner field types of nested POJOs.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# nested-pojo-type-key-validation

## Instructions

# Nested POJO Type Key Validation

## Instructions

- WHEN the TG encounters code that validates field types for key expressions on nested POJO fields (e.g., `ExpressionKeys` selecting fields like `"f0.myField"` where `myField` is of a complex type such as `Tuple2` or another non-comparable type)
- THEN the TG should write a test that:
  1. Creates a tuple type where one field is a POJO that contains a field of a non-comparable type (e.g., `Tuple2<Integer, Integer>`)
  2. Attempts to construct an `ExpressionKeys` object with a key expression that selects that nested field (e.g., `"f0.tupleField"`)
  3. Verifies that an `IllegalArgumentException` is thrown (the buggy version fails to detect the invalid type and allows the construction, causing downstream failures)
- The test should NOT test with a valid comparable field type (like `String` or `int`) — only with an invalid nested type
- Common pitfall: Testing only the top-level field types of the tuple itself (e.g., checking `f0` type is a POJO) but not traversing into the nested POJO's fields to validate their types. The TG might also forget to call methods like `assertThat(thing, hasProperty(...))` and instead test the fix behavior incorrectly.

**Incorrect test approach (doesn't catch the bug):**
```java
// This only checks that a TOP-LEVEL tuple field type is valid — doesn't test the nested POJO field
try {
    new ExpressionKeys<>("f0", tupleTypeInfo);
    // No assertion — silently succeeds even if f0's inner field is invalid
} catch (IllegalArgumentException e) {
    // Won't catch that f0.tupleField type was never validated
}
```

**Correct test approach (catches the bug):**
```java
@Test(expected = IllegalArgumentException.class)
public void testTupleWithNestedPojo() {
    // Create a Tuple2<Integer, Integer> type for the nested field
    TypeInformation<?> nestedType = new TupleTypeInfo<>(BasicTypeInfo.INT_TYPE_INFO, BasicTypeInfo.INT_TYPE_INFO);
    
    // Create a POJO type where one field is a Tuple2 (not a valid key type)
    TypeInformation<?> pojoType = new PojoTypeInfo(MyPojo.class, new ArrayList<>());
    
    // Create a Tuple2<MyPojo, String> type
    TypeInformation<?> tupleType = new TupleTypeInfo<>(pojoType, BasicTypeInfo.STRING_TYPE_INFO);
    
    // This should throw IllegalArgumentException because f0.tupleField is a Tuple2 type
    new ExpressionKeys<>("f0.tupleField", tupleType);
}
```

- The test should expect `IllegalArgumentException` with a message indicating the field type is not a valid key type
- Verify that the exception is thrown during ExpressionKeys construction (not later during runtime usage)