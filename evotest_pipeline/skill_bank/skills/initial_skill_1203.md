---
name: alternative-protocol-decoding-paths
description: WHEN a protocol decoder has multiple decoding paths or frame decoder
  fallback logic, THEN test each alternative path with valid data to ensure no path
  throws unexpected exceptions or returns incomplete data. This skill applies to protocol
  frame decoders with branching logic for different message formats.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-paths

## Instructions

# Alternative Protocol Decoding Paths

## Instructions

- WHEN the TG encounters a protocol decoder that has **alternative decoding paths** (e.g., an `if`-`else` branch, a `switch` statement, or a try-catch fallback that tries a different decoding approach for the same message type)
- THEN the TG should write **parametric tests** that construct input buffers for **each alternative path** and verify:
  1. No exception is thrown
  2. The decoded result is non-null and has the expected structure (e.g., position/lat/lon values, valid checksums)
  3. Each path produces consistent results for equivalent inputs

- **Concrete example**: If the decoder has logic like `if (condition) { decodeTypeA(...) } else { decodeTypeB(...) }`, test both branches by crafting buffers that satisfy and fail the condition.

- **Common pitfalls**:
  - Testing only the "happy path" (the most common branch) and missing the fallback/alternative branch
  - Assuming that because one branch works, the other branch also works — the bug often hides in the less-tested path
  - Using invalid/random data for alternative paths instead of valid structured data that exercises that specific branch

- **What to verify on the buggy version**: The alternative decoding path may throw an unexpected exception (e.g., `IndexOutOfBoundsException`, `NullPointerException`, `IllegalArgumentException`) or return `null`/incomplete data when it should return a valid decoded message.

- **Correct test approach**:
  ```java
  // Test for each alternative decoding path
  @Test
  public void testDecodePathA() {
      // Craft buffer that triggers path A
      ByteBuf buf = Unpooled.copiedBuffer(/* valid data for path A */);
      // ... verify decoded result
  }
  
  @Test
  public void testDecodePathB() {
      // Craft buffer that triggers path B
      ByteBuf buf = Unpooled.copiedBuffer(/* valid data for path B */);
      // ... verify decoded result  
  }
  ```

- **Incorrect approach**:
  ```java
  // Testing only with one buffer type, missing alternative paths
  @Test
  public void testDecode() {
      // Only tests the default/common branch
      ByteBuf buf = Unpooled.copiedBuffer("default-format-data");
      // ...
  }
  ```