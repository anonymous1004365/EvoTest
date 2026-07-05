---
name: pojo-field-generic-type-stripping
description: Covers the bug where PojoTypeInfo.getTypeAt() strips generic type information
  from PojoField.getTypeInformation(), causing ClassCastException or InvalidFieldReferenceException.
  Use when testing POJO field access with generic types (e.g., Vertex<Long, Double>).
code_tags:
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# pojo-field-generic-type-stripping

## Instructions

# Pojo Field Generic Type Stripping

## Instructions

- WHEN the TG encounters code that creates a `PojoTypeInfo` for a POJO class whose fields are parameterized with generic types (e.g., `Vertex<Long, Double>` which has a field `value` of type `Long`, `key` of type `Double`, or a generic field like `List<String>`):
  
  THEN the TG should write a test that calls `PojoTypeInfo.getTypeAt(fieldIndex)` for each field index of the POJO and verify that the returned `TypeInformation` preserves the concrete generic type arguments (e.g., `BasicTypeInfo.LONG_TYPE_INFO`, `BasicTypeInfo.DOUBLE_TYPE_INFO`, or `ListTypeInfo` with correct element type), not just the raw (erased) type class.

- WHEN testing the buggy code path (no fix applied):
  
  THEN the TG should expect an `IllegalStateException`, `InvalidFieldReferenceException`, or `ClassCastException` to be thrown when trying to use the POJO type information derived from a class with generic fields (like `Vertex<Long, Double>`), because `PojoTypeInfo.getTypeAt()` returns a `TypeInformation` that has lost its generic parameters.

- Common pitfalls:
  - Testing only with simple POJOs (no generic type parameters on fields) — the bug only manifests when fields have generic type arguments that get stripped.
  - Testing `TypeExtractor.getForClass(PojoClass.class)` without then accessing individual field types via `PojoTypeInfo.getTypeAt(index)` — the bug is triggered when field-level type information is retrieved from the PojoTypeInfo.
  - Using `getFieldNames()` to verify field existence without checking the actual `TypeInformation` of each field.

### Example (WRONG — passes on both buggy and fixed code):
```java
// Does NOT trigger the bug — no field type access
PojoTypeInfo<MyPojo> typeInfo = (PojoTypeInfo<MyPojo>) TypeExtractor.getForClass(MyPojo.class);
// Only checks field names, not their types
assertArrayEquals(new String[]{"field1", "field2"}, typeInfo.getFieldNames());
```

### Example (CORRECT — catches the bug):
```java
// Triggers the bug — accesses field-level type information from PojoTypeInfo
PojoTypeInfo<VertexTyped> typeInfo = (PojoTypeInfo<VertexTyped>) TypeExtractor.getForClass(VertexTyped.class);
TypeInformation<?> fieldType = typeInfo.getTypeAt(0);  // throws IllegalStateException on buggy version
// or the test should expect the exception on buggy and verify correct type on fixed
```