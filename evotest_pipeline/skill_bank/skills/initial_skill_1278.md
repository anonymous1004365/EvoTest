---
name: generic-array-type-erasure-mutation
description: When a method mutates a generic collection/array parameter's elements
  and the element type depends on erased generic type parameters, test that elements
  of different concrete types that map to the same erased type are all handled correctly.
  The TG should verify the buggy version throws an exception or produces wrong output
  when mixing types.
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# generic-array-type-erasure-mutation

## Instructions

# Generic Array Type Erasure Mutation

## Instructions

- WHEN the TG encounters a method that accepts a generic array or collection parameter (e.g., `T[]`, `List<T>`) and mutates/transforms elements **and** the method relies on runtime checks like `instanceof` or `Class.isAssignableFrom` that are affected by type erasure
- THEN the TG should construct a parametric test (using `@ParameterizedTest` or a loop over test cases) that:
  1. Provides inputs of **two different concrete types** that both satisfy the same erased bound (e.g., both `String` and `Integer` when `T` is unbounded and erases to `Object`)
  2. Calls the method-under-test with these mixed-type inputs
  3. Asserts that the correct transformation/processing occurs for each element
  4. Verifies the method does NOT silently skip, corrupt, or throw unexpected `ClassCastException` for either type
  5. If the bug is a silent failure (e.g., returns without processing some types), assert the expected output matches for all types

- **Common pitfalls to avoid**:
  - Testing only one type (e.g., only `String` elements) when the generic method should handle multiple types
  - Assuming type erasure makes all elements behave identically at runtime — code may still do `instanceof` checks that discriminate between concrete types
  - Not providing a mixed-type collection (e.g., `List<Object>` containing both `String` and `Integer` instances) as input
  - Forgetting to test the **boundary case** where a type is used that the buggy code does NOT explicitly check for (e.g., only checks for `String` but `Integer` is also valid)

- **Example (correct approach)**:
```
// Given a method: public static <T> T[] filterInvalid(T[] input)
// Buggy version only handles String elements; Integer elements cause ClassCastException

@Test
void testFilterInvalidMixedTypes() {
    Object[] mixed = new Object[] { "hello", 42, "world", 99 };
    assertDoesNotThrow(() -> {
        Object[] result = SomeClass.filterInvalid(mixed);
        // Verify both String and Integer elements are preserved/processed
        assertTrue(result.length > 0);
        assertTrue(Arrays.stream(result).anyMatch(e -> e instanceof String));
        assertTrue(Arrays.stream(result).anyMatch(e -> e instanceof Integer));
    });
}
```

- **Example (incorrect approach)**:
```
// BAD: Only tests with String elements
@Test
void testFilterInvalid() {
    String[] input = new String[] { "hello", "world" };
    String[] result = SomeClass.filterInvalid(input); // passes, but misses Integer bug
    assertEquals(2, result.length);
}
```

- **What to expect on the buggy version**: The test should produce a `ClassCastException`, `ArrayStoreException`, or incorrect output/ordering when elements of an unexpected concrete type are present. The fixed version should handle all types uniformly.