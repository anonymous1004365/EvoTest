---
name: byte-array-short-put-roundtrip
description: When writing short values into byte arrays using putShort, the TG should
  verify roundtrip correctness for boundary and negative values, because array capacity
  and value overflow can cause silent corruption.
code_tags:
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# byte-array-short-put-roundtrip

## Instructions

# Byte Array Short Put Roundtrip

## Instructions

- WHEN the TG encounters a method that writes a `short` value into a byte array (e.g., `putShort` or similar), and the method takes an index and a `short` (or `int` that gets cast to `short`) as parameters
- THEN the TG should write a **roundtrip test** that writes a series of short values into the byte array at specific offsets, then reads them back and asserts they match. Test with **boundary values**: `Short.MIN_VALUE` (-32768), `Short.MAX_VALUE` (32767), `0`, `-1`, `1`, and values that might overflow int-to-short casting (e.g., an `int` value like `65535` or `-100000` that when cast to `short` produces a valid short). Also verify that writing beyond the array capacity throws `IndexOutOfBoundsException`.
- The TG should verify that the **array capacity is checked** before writing — i.e., `index + 2 <= array.length`. If the method accepts an `int` that gets cast to `short`, also verify that **overflow behavior** (e.g., `(short) someInt`) preserves the correct value after a roundtrip.
- Mistakes to avoid: (1) Testing only `0` or non-negative values — negative shorts are the most common failure. (2) Assuming int-to-short overflow is handled correctly without testing it. (3) Not verifying that the index is bounded correctly — i.e., `idx` and `idx+1` are within the array. (4) Testing only a single value — use a parametric approach with a small set of carefully chosen values.

```java
// CORRECT: Parametric roundtrip test for short put
@ParameterizedTest
@ValueSource(ints = {Short.MIN_VALUE, Short.MAX_VALUE, 0, -1, 1, 65535, -100000, 42})
void testShortRoundtrip(int value) {
    byte[] arr = new byte[4];
    short original = (short) value; // simulate the cast that happens in the method
    putShort(arr, 0, original);
    short result = getShort(arr, 0);
    assertEquals(original, result, "Roundtrip failed for value " + original);
}

// CORRECT: Array bounds check
@Test
void testShortPutOutOfBounds() {
    byte[] arr = new byte[2];
    assertThrows(IndexOutOfBoundsException.class, () -> putShort(arr, 1, (short) 42));
}
```

```java
// INCORRECT: Only testing non-negative values — misses negative short bug
@Test
void testShortRoundtrip() {
    byte[] arr = new byte[4];
    putShort(arr, 0, (short) 42);
    assertEquals(42, getShort(arr, 0)); // passes even if negative values fail
}

// INCORRECT: Not testing boundary — might miss overflow bug
@Test
void testShortRoundtrip() {
    byte[] arr = new byte[4];
    putShort(arr, 0, (short) 65535); // int literal, cast to short = -1
    assertEquals(-1, getShort(arr, 0)); // but test expects 65535 (wrong expectation)
}
```