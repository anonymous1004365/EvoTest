---
name: defaultValue-serialization-validation
description: ''
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# defaultValue-serialization-validation

## Instructions

# Default Value Serialization Validation

## Instructions

- WHEN the TG encounters a `StateDescriptor` subclass (e.g., `ValueStateDescriptor`) that:
  - Has a `getDefaultValue()` method returning a serializable object
  - The default value is stored as a field (e.g., `T defaultValue`)
  - The descriptor may be serialized/deserialized (e.g., via Java `Serializable`, `readObject()`, `writeObject()`, or copy constructor)
  - The default value can be set to a very large or non-null value

- THEN the TG should write a test that:
  1. Creates a `ValueStateDescriptor` (or similar `StateDescriptor` subclass) with a very large default value (e.g., a `byte[]` of size > 2^15 or > 2^16 bytes)
  2. Invokes a copy, serialize/deserialize, or `deepCopy()` operation that internally serializes the default value
  3. Expects the copy/deserialized result to have the same default value as the original (equal, not just non-null)
  4. Expects the operation to complete successfully without `NegativeArraySizeException`, `ArrayIndexOutOfBoundsException`, or `IOException` caused by buffer overflow

- Concrete example from actual bug:
  - The bug was triggered when `ValueStateDescriptor` with a `byte[]` default value of size 100_000 bytes (~97KB) was copied
  - The internal serialization buffer (e.g., `DataOutputViewStreamWrapper` or `DataInputView`) used a 16-bit length field for the byte array, causing truncation or `NegativeArraySizeException` when the size exceeded `Short.MAX_VALUE` (32767) or some other 16-bit limit
  - The fix involved ensuring the serialization uses an integer length field (32-bit) instead of a short (16-bit) when writing/reading the default value's byte representation

- Common pitfalls:
  - Testing only with small default values (e.g., empty strings, single-byte arrays) — these will not trigger the overflow bug
  - Testing only that no exception is thrown without also verifying the deserialized value equals the original — a silent truncation could also occur
  - Forgetting to test with `null` default values — the code path for null vs non-null defaults may differ
  - Testing only `String` default values when the descriptor can hold `byte[]` or other types with different serialization logic

- Incorrect test (too weak):
  ```java
  @Test
  public void testDefaultValue() {
      ValueStateDescriptor<byte[]> desc = new ValueStateDescriptor<>("test", byte[].class, new byte[10]);
      assertEquals(10, desc.getDefaultValue().length);
  }
  ```

- Correct test (catches the bug):
  ```java
  @Test
  public void testVeryLargeDefaultValue() {
      byte[] largeDefault = new byte[100_000];
      ValueStateDescriptor<byte[]> desc = new ValueStateDescriptor<>("test", byte[].class, largeDefault);
      
      ValueStateDescriptor<byte[]> copy = desc.deepCopy(); // or serialize/deserialize
      
      // Verify no exception and value is preserved
      assertArrayEquals(largeDefault, copy.getDefaultValue());
  }
  ```