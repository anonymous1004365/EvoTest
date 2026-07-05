---
name: missing-frame-decoder-alternative-path
description: When a protocol decoder has an alternative frame decoding path (e.g.,
  fallback or secondary decoder), the TG should verify that both paths produce consistent
  frame boundaries. Without this check, one path may incorrectly consume trailing
  bytes, shift frame offsets, or fail to reset position, corrupting subsequent decoding.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# missing-frame-decoder-alternative-path

## Instructions

# Missing Frame Decoder Alternative Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses an **alternative frame decoding path** (e.g., a fallback decoder invoked when the primary decoder fails, a secondary method that parses frame length differently, or any `if/else` branch that computes frame boundaries via a different formula)
- THEN the TG MUST write a **parametric test** that exercises both the primary and alternative frame decode paths with the same input data. The test should verify that:
  1. Both paths produce the **same decoded message content** (or at minimum, the same frame boundaries).
  2. No **trailing bytes are silently consumed** by one path but not the other.
  3. The decoder's internal state (position, offset, buffer pointers) is correctly **reset** or consistently handled after each path.
  4. If the alternative path is a fallback (only reached on failure), test with **valid data that triggers the fallback** (e.g., a corrupt or partial message that the primary decoder rejects but the alternative accepts).
- Common pitfalls to avoid:
  - Testing only the primary decoder path (happy path) and assuming the fallback is equivalent.
  - Not testing with **edge case inputs** that exercise the boundary between the two paths (e.g., a message that is almost-but-not-quite valid for the primary path).
  - Forgetting to verify that **no data corruption** occurs when switching between paths mid-stream (e.g., if fallback is used for one message and primary for the next).
  - Assuming that because both paths produce a result, the results are semantically identical.

### Example (correct)

```java
@Test
public void testAlternativeFrameDecode() {
    // Given: a byte buffer that triggers the primary decoder path
    byte[] primaryData = ...; // assembles a valid frame for primary path
    // And: the same buffer content but with a leading byte that forces fallback
    byte[] fallbackData = ...; // same payload but triggers secondary decoder
    
    // When: decoding both
    NavisProtocolDecoder decoder = new NavisProtocolDecoder();
    decoder.decode(null, null, Unpooled.wrappedBuffer(primaryData));
    decoder.decode(null, null, Unpooled.wrappedBuffer(fallbackData));
    
    // Then: the produced messages are equivalent
    // (e.g., same position, same number of decoded objects, no leftover bytes)
}
```

### Example (incorrect — only tests primary path)

```java
@Test
public void testDecode() {
    // BAD: Only tests the primary decoder path
    byte[] data = ...; // valid frame for primary path
    NavisProtocolDecoder decoder = new NavisProtocolDecoder();
    Object result = decoder.decode(null, null, Unpooled.wrappedBuffer(data));
    assertNotNull(result);
    // Missing: no test for alternative frame decode path
}
```