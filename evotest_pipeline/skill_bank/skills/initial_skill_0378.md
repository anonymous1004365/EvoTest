---
name: composite-unsigned-integer-construction-validation
description: ''
code_tags:
- VALIDATION
- OVERFLOW
test_pattern: EXCEPTION_TEST
---

# composite-unsigned-integer-construction-validation

## Instructions

# Composite Unsigned Integer Construction Validation

## Instructions

- WHEN the TG encounters a composite unsigned integer class that splits a large numeric value (e.g., `BigInteger`) into a **low** and **high** component — for example, `CompUInt128` constructed from a `BigInteger` value and decomposed into `low` (lower 64 bits, as `CompUInt64`) and `high` (upper 64 bits, as `CompUInt64`) — and the constructor **does not apply a bit mask** to discard bits beyond the combined bit length before splitting:
  - THEN the TG should write a test that supplies a value whose bit length **exceeds the combined bit length** of the composite type. For example, for `CompUInt128` (128-bit total), supply a `BigInteger` value that requires more than 128 bits to represent (e.g., `BigInteger.ONE.shiftLeft(128)`, `BigInteger.ONE.shiftLeft(200)`, or `new BigInteger("340282366920938463463374607431768211456")` which equals 2^128).
  - The test should verify that:
    1. The constructor **throws an exception** (e.g., `IllegalArgumentException`, `ArithmeticException`) for out-of-range values, **OR**
    2. If the constructor silently masks, the test should call a method that computes with the value (e.g., `toBigInteger()`, `toString()`, or an arithmetic operation) and assert that the result is **correctly masked/moduloed** to the valid range — i.e., `value.mod(2^bitLength)`.

- WHEN the constructor does **not** validate or mask and instead passes the full value into the low/high components (which themselves may overflow silently), expect that the **buggy version produces incorrect results** (e.g., garbage in the high component) while the **fixed version** properly masks or validates.

- **Common pitfalls**:
  - Testing only values that fit within the composite type's range (e.g., values below 2^128 for CompUInt128) — these pass on both buggy and fixed versions and miss the bug.
  - Testing only the low component type's range (e.g., only values below 2^64 for CompUInt128) — these also miss the bug.
  - Assuming that `BigInteger` constructors or shift operations guarantee correctness without explicit masking — they do not; the composite constructor must do its own bounds check.
  - Writing a non-parametric test with only one specific out-of-range value — instead, use a parameterized test with several boundary values: `2^bitLength`, `2^bitLength + 1`, `2^bitLength * 2`, etc.

### Correct Example (should detect the bug)
```java
@Test(expected = IllegalArgumentException.class)
public void testConstructWithOverflow() {
    BigInteger overflowValue = BigInteger.ONE.shiftLeft(128); // 2^128, exceeds 128-bit range
    new CompUInt128(overflowValue);
}
```

### Wrong Example (would miss the bug)
```java
@Test
public void testConstructValid() {
    BigInteger validValue = BigInteger.ONE.shiftLeft(64); // fits in 128 bits
    CompUInt128 val = new CompUInt128(validValue);
    assertEquals(validValue, val.toBigInteger()); // passes on both buggy and fixed
}
```