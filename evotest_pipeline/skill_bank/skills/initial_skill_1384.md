---
name: alternative-protocol-decoding-null-check
description: When a protocol decoder has an alternative decoding path (e.g., if-else
  branches based on position or channel type), the TG must test both branches separately.
  The alternative branch may silently return null or fail to decode, causing NPE downstream.
  Always verify that all branches produce a non-null decoded result.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-null-check

## Instructions

# Alternative Protocol Decoding — Null Check

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `extends ProtocolDecoder` or `extends BaseFrameDecoder`) that has two or more decoding branches — such as an `if (position > 0)` / `else` pattern, or an `if (channel instanceof X)` / `else` pattern
- THEN the TG **must** write a parametric test (e.g., `@ParameterizedTest` or a `@Test` with multiple calls) that exercises **each alternative branch separately** with input data that triggers that specific branch. For each branch, verify the decoded result is **not null**. If the branch decodes into a collection, verify the collection is **not empty**.
- Include concrete test inputs that cause the decoder to take the **non-primary** branch (the branch that is not the main happy path). For example, if the decoder uses `if (position > 0)` to decide between two different decoding strategies, test with `position == 0` (or with data that produces that condition) to verify the alternative branch works.
- **Common pitfall**: Testing only the first/primary branch with well-formed data. The TG must not assume the alternative branch is correct — it may return `null` or produce an empty result, which leads to a `NullPointerException` or empty-protocol error in the caller.
- **Example (correct)**:
  ```java
  @ParameterizedTest
  @CsvSource({
      "0f, 010203, true",    // alternative branch: position == 0
      "1f, 040506, true"     // primary branch: position > 0
  })
  public void testDecodeBothBranches(float position, String data, boolean success) {
      // Build input buffer that triggers the given branch
      // Invoke decoder.decode(...)
      // Assert that result is NOT null
  }
  ```
- **Example (incorrect / common pitfall)**:
  ```java
  @Test
  public void testDecodeWithPosition() {
      // Only tests position > 0 branch
      // Does NOT test the else/alternative branch
  }
  ```