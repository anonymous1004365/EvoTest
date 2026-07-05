---
name: alternative-protocol-decoding-path-validation
description: When a protocol decoder's frame decoder has an alternative decoding path (e.g., using a different decoder or method when the primary path fails), tests must exercise both paths with varied input types to ensure state is correctly managed and no ClassCastException or decoding failure occurs.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'BOUNDARY_CHECK']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path-validation

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol frame decoder (e.g., a class extending `FrameDecoder` or using `CodecFactory`) that has an **alternative decoding path** — such as calling a secondary decoder method (e.g., "decode with decoder type X, and if that fails, fall back to decoder type Y"), or passing different `DecoderResult` types to different decoder instances
- THEN the TG should write a test that **exercises both decoding paths** with **each path's expected input type**, and verify:
  1. That the alternative path does **not** throw a `ClassCastException` or produce corrupted output
  2. That the decoder correctly handles inputs of the expected type for each path (e.g., `String` vs custom types like `CtTypeReference`)
  3. That internal state (e.g., a "last decoded value" field) is properly updated after each path's execution

- **Common pitfalls to avoid:**
  - Testing only the primary/expected decoding path while ignoring the alternative/fallback path
  - Assuming all inputs to the decoder are of a single type (e.g., `String`) when the alternative path operates on a different type (e.g., a custom class like `CtTypeReference`)
  - Not verifying that internal state fields (e.g., `lastDecoded`) are correctly set after the alternative path executes
  - Using only simple string inputs when the decoder may also receive typed objects from the alternative decoder

- **Concrete example (correct):** For a `MyProtocolDecoder` with a `decode` method that uses `decoderA.decode(channel, buf)` as primary and `decoderB.decode(channel, buf)` as alternative:
  ```java
  @Test
  public void testAlternativeDecodingPath() {
      MyProtocolDecoder decoder = new MyProtocolDecoder();
      
      // Primary path input type (e.g., String)
      Object primaryInput = "test";
      Object result1 = decoder.decode(primaryInput);
      assertNotNull("Primary path should return non-null", result1);
      
      // Alternative path input type (e.g., CtTypeReference)
      Object altInput = new CtTypeReference("test");
      Object result2 = decoder.decode(altInput);
      assertNotNull("Alternative path should return non-null", result2);
      // Also verify internal state is updated
      assertEquals("State should reflect last decoded value", altInput, decoder.getLastDecoded());
  }
  ```

- **Concrete example (incorrect):**
  ```java
  @Test
  public void testDecode() {
      MyProtocolDecoder decoder = new MyProtocolDecoder();
      // Only testing String input — misses the alternative path
      assertEquals("expected", decoder.decode("test"));
  }
  ```

- **What to expect on buggy version:** The test should fail on the buggy version, typically with a `ClassCastException` thrown when the alternative path receives an unexpected type, or with incorrect internal state (e.g., `null` or stale value) after the alternative path executes.