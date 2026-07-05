---
name: array-key-selector-autoboxing-type-mismatch
description: Use when testing ArrayKeySelector.getKey() on arrays of boxed types (e.g.
  Integer[], int[]). The java.lang.reflect.Array.get() returns boxed objects, but
  when used with a TupleTypeInfo wrapping a BasicArrayTypeInfo, the setField method
  may expect the primitive type, causing ClassCastException. Test with both boxed
  and primitive array types to verify correct key extraction.
code_tags:
- BOUNDARY_CHECK
- TYPE_CONVERSION
- ARRAY_INDEX_ACCESS
- ARRAY_REFLECTION_RETRIEVAL
- ARRAY_BOXING_REFLECTION
test_pattern: EXCEPTION_TEST
---

# array-key-selector-autoboxing-type-mismatch

## Instructions

# Array KeySelector Autoboxing Type Mismatch

## Instructions

- WHEN the test code involves `KeySelectorUtil.ArrayKeySelector` extracting keys from arrays (like `String[]`, `int[]`, `Integer[]`) using `java.lang.reflect.Array.get()` and setting them into a `Tuple` via `Tuple.setField()`
- THEN write a test that verifies that `ArrayKeySelector.getKey()` works correctly for **both**:
  1. **Primitive arrays** (e.g., `int[]`, `long[]`, `float[]`) accessed via `PrimitiveArrayTypeInfo` — `Array.get()` returns boxed types (e.g., `Integer` for `int`), but the tuple and its `TypeInformation` expect the **primitive** type. On the buggy version, this can cause a `ClassCastException` at runtime.
  2. **Object/boxed arrays** (e.g., `String[]`, `Integer[]`) accessed via `BasicArrayTypeInfo` — `Array.get()` returns the object directly.

- Specifically, for **primitive arrays** (e.g., `int[]` with `PrimitiveArrayTypeInfo.INT_PRIMITIVE_ARRAY_TYPE_INFO`):
  - Create an `ArrayKeySelector<int[]>` using `KeySelectorUtil.getSelectorForArray(new int[] {1}, PrimitiveArrayTypeInfo.INT_PRIMITIVE_ARRAY_TYPE_INFO)`
  - Call `getKey()` on an array like `new int[]{1, 2, 3, 4, 5}`
  - The resulting `Tuple1` should contain the boxed equivalent (e.g., `Integer.valueOf(2)`)
  - Verify the result using `assertEquals(new Tuple1<>(2), selector.getKey(array))` — this should succeed on the fixed version; on the buggy version it may throw `ClassCastException` because `Array.get()` returns `Integer` but the tuple type info expects `int`

- ALSO test **object arrays** (e.g., `String[]` with `BasicArrayTypeInfo.STRING_ARRAY_TYPE_INFO`):
  - These should work on both buggy and fixed versions since the types are already object types
  - Use `KeySelectorUtil.getSelectorForArray(new int[] {1}, BasicArrayTypeInfo.STRING_ARRAY_TYPE_INFO)`
  - Call `getKey()` on `new String[]{"a", "b", "c", "d", "e"}`
  - Expect `new Tuple1<>("b")`

- Common pitfalls to avoid:
  - ❌ Testing only object arrays (e.g., `String[]`) and not primitive arrays (e.g., `int[]`) — the bug only manifests with primitive arrays
  - ❌ Assuming `Array.get()` returns the same type as the array component type — for primitive arrays, `Array.get()` returns boxed wrapper types (e.g., `Integer` instead of `int`)
  - ❌ Not catching `Exception` in the test — `ArrayKeySelector.getKey()` throws `Exception` which needs to be handled
  - ❌ Forgetting to check both single-field and multi-field selectors (positions like `new int[]{1}` vs `new int[]{3, 0}`)

### Correct Example:
```java
// Test primitive int[] array — catches the autoboxing bug
@Test
public void testPrimitiveArrays() {
    int[] array1 = { 1, 2, 3, 4, 5 };
    int[] array2 = { -5, -4, -3, -2, -1, 0 };

    KeySelectorUtil.ArrayKeySelector<int[]> singleFieldSelector =
            KeySelectorUtil.getSelectorForArray(
                    new int[] {1},
                    PrimitiveArrayTypeInfo.INT_PRIMITIVE_ARRAY_TYPE_INFO);

    assertEquals(new Tuple1<>(2), singleFieldSelector.getKey(array1));
    assertEquals(new Tuple1<>(-4), singleFieldSelector.getKey(array2));

    KeySelectorUtil.ArrayKeySelector<int[]> twoFieldsSelector =
            KeySelectorUtil.getSelectorForArray(
                    new int[] {3, 0},
                    PrimitiveArrayTypeInfo.INT_PRIMITIVE_ARRAY_TYPE_INFO);

    assertEquals(new Tuple2<>(4, 1), twoFieldsSelector.getKey(array1));
    assertEquals(new Tuple2<>(-2, -5), twoFieldsSelector.getKey(array2));
}
```

### Incorrect Example (only tests object arrays, misses the bug):
```java
// ❌ Tests only String[] arrays — won't catch the primitive array bug
@Test
public void testObjectArraysOnly() {
    String[] array1 = { "a", "b", "c", "d", "e" };

    KeySelectorUtil.ArrayKeySelector<String[]> selector =
            KeySelectorUtil.getSelectorForArray(
                    new int[] {1},
                    BasicArrayTypeInfo.STRING_ARRAY_TYPE_INFO);

    assertEquals(new Tuple1<>("b"), selector.getKey(array1));
    // This passes on BOTH buggy and fixed — does NOT detect the bug!
}
```