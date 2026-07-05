---
name: generic-type-resolution-for-raw-types
description: ''
code_tags:
- GENERIC_TYPE_RESOLUTION
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# generic-type-resolution-for-raw-types

## Instructions

# Generic Type Resolution for Raw Types

## Instructions

- WHEN the TG encounters a property/field whose declared type involves generics (e.g., `List`, `Map`, `Set`, or an array type like `byte[]`) and the type resolution logic calls methods like `getTypeInformation()`, `getActualType()`, `getResolvedType()`, or `resolve(Type)` to determine the concrete type argument
- THEN the TG should write parametric tests that:
  - Create a property with a **raw type** (e.g., `List field`, `Map field`, `Set field`, without angle brackets)
  - Verify that the generic type resolution does **not** throw a `NullPointerException` or return `null` when resolving the type of the raw field
  - For raw `List` fields, assert that `getTypeInformation().getActualType().getType()` correctly returns `List.class` (not `null` and not Object.class)
  - For raw `Map` fields, assert that the resolved type correctly identifies the map entry types
  - For `byte[]` (array) fields, verify that the resolved property type correctly identifies the component type as `byte.class`

- Common pitfalls to avoid:
  - Testing only with parameterized types (e.g., `List<String>`) and forgetting to test **raw types** (e.g., just `List`). Raw types are a common source of NPEs and null returns in generic resolution code.
  - Assuming that `getActualType()` always returns a non-null value — it can return `null` for raw types in buggy implementations.
  - Testing only `String` or reference type generics — also test with `byte[]` (primitive arrays) which are a special case.
  - Forgetting that array types like `byte[]` use `Class<?>` with `isArray() == true`, requiring the resolution logic to handle `getComponentType()` correctly.

- Correct approach example (what to test):
```java
// Test raw List type resolution
public static class RawListSample {
    List rawList;
}
// Verify: typeInfo.getActualType().getType() returns List.class, not null

// Test raw Map type resolution
public static class RawMapSample {
    Map rawMap;
}
// Verify: typeInfo.getActualType().getType() returns Map.class, not null

// Test byte[] array type resolution
public static class ByteArraySample {
    byte[] data;
}
// Verify: typeInfo.getActualType().isArray() is true, getComponentType() is byte.class
```

- Incorrect approach example (what test generators often write):
```java
// WRONG: Only tests List<String>, missing the raw List case
public static class TypedListSample {
    List<String> typedList;
}
// WRONG: Assumes getActualType() can never be null, missing null-check assertions
// WRONG: Doesn't test byte[] or other array types
```

- The test should assert that:
  - No `NullPointerException` is thrown during type resolution
  - `getTypeInformation().getActualType()` returns a non-null `TypeInformation`
  - `getTypeInformation().getActualType().getType()` returns the correct `Class<?>` (e.g., `List.class`, `Map.class`, or the array class)