---
name: alternative-protocol-decoding-path
description: When a frame decoder has a secondary/alternative decoding path (e.g., a "try" block that falls through to a different decoder when the primary path fails), test that this alternative path correctly decodes valid frames. Without explicit tests covering this path, code changes may silently break the alternative decoding logic.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

- WHEN the TG encounters a frame decoder that contains a `try...catch` block or conditional logic that switches between two different decoding strategies (e.g., first attempting one decoder and, on failure or specific condition, falling through to another decoder)
- THEN the TG MUST write a test that exercises BOTH decoding paths individually:
  1. Test the primary/protocol-specific decoder path (e.g., `AplicomProtocolDecoder`) with a frame that goes through the normal path.
  2. Test the alternative/generic decoder path (e.g., `IoBuffer`-based or `StringDecoder`-based fallback) with a frame that triggers that path.
- The test should verify that each path produces a correct, non-null decoded result, and that no unexpected exceptions are thrown during the alternative path.
- Common pitfalls:
  - Testing only the primary protocol decoder and assuming the fallback path "just works" because it's simple.
  - Assuming the alternative decoder logic is invariant across code changes — it is NOT, especially when shared buffer/offset logic is refactored.
  - Not providing input data that is specifically crafted to exercise the alternative path (e.g., a frame that triggers the catch or the else-branch).
  - Forgetting to test that the alternative path returns the expected decoded object type or structure, not just that it doesn't crash.
- Example correct test approach (pseudocode):
  ```java
  // Test the alternative/generic decoding path
  ByteBuf buf = Unpooled.copiedBuffer(/* bytes that reach the else/catch branch */);
  Object decoded = decoder.decode(null, null, buf);
  assertNotNull("Alternative path should decode successfully", decoded);
  // Optionally verify it's the expected type
  ```
- Example incorrect test approach:
  ```java
  // Only test the primary path — alternative path coverage is missing
  ByteBuf buf = Unpooled.copiedBuffer(/* bytes that take the primary path only */);
  Object decoded = decoder.decode(null, null, buf);
  assertNotNull(decoded);
  ```