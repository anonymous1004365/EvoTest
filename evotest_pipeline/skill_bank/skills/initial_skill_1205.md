---
name: alternative-protocol-frame-decoding
description: When a protocol decoder has an alternative (if/else or fallback) decoding
  path that mutates state differently than the primary path, test both branches with
  varying payload types to ensure frame boundaries and buffer offsets are handled
  consistently.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-frame-decoding

## Instructions

# Alternative Protocol Frame Decoding

## Instructions

WHEN the TG encounters a protocol frame decoder that:
- Has an `if/else` or alternative branch in its decoding logic (e.g., checking whether a buffer contains a certain message type or format)
- Returns a decoded message or mutates decoder state (buffer position, offset) differently in each branch
- Processes the payload using offset/position operations (e.g., `readerIndex`, `writerIndex`, `skipBytes`, `readUnsignedByte`)

THEN the TG should:
1. Write a parametric test that exercises **each alternative branch** of the decoding logic, varying the payload content or type
2. For **each branch**, assert that:
   - The method returns a non-null result
   - The decoder state (buffer position, frame boundaries) is consistent — no `IndexOutOfBoundsException` or similar corruption
   - The decoded message content matches expectations for that branch
3. Include at least one test input that triggers the **primary** path and one that triggers the **alternative** path — do not test only one branch
4. Verify that the decoder does not skip, lose, or misparse data from the payload, especially around the branch decision point (e.g., the first byte/flag that determines which branch is taken)

Common pitfalls to avoid:
- **Testing only the primary (most common) decoding branch** — the bug may live entirely in the alternative branch
- **Using only a single message type** — multiple types may be needed to exercise all branches
- **Forgetting to verify buffer state after decoding** — the fix may involve offset/position correction in one branch
- **Testing with only String parameters** when the decoder actually branches on a numeric type flag (e.g., `CtTypeReference` vs `String`)

### Correct Example (Testing Both Branches)
```java
// When the decoder branches on the first byte as a type flag:
@Test
public void testDecodeBothBranches() {
    // Branch 1: Type flag = 1 (primary path — e.g., String parameter)
    ByteBuf buf1 = Unpooled.copiedBuffer(new byte[]{0x01, 0x00, 0x05, 'h', 'e', 'l', 'l', 'o'});
    Object result1 = decoder.decode(ctx, buf1);
    assertNotNull(result1);
    assertEquals(0, buf1.readableBytes()); // buffer fully consumed

    // Branch 2: Type flag = 2 (alternative path — e.g., numeric/long parameter)
    ByteBuf buf2 = Unpooled.copiedBuffer(new byte[]{0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2A});
    Object result2 = decoder.decode(ctx, buf2);
    assertNotNull(result2);
    assertEquals(0, buf2.readableBytes()); // buffer fully consumed
}
```

### Incorrect Example (Testing Only One Branch)
```java
// BUG: Only tests the primary (String type) branch — never triggers the alternative branch
@Test
public void testDecodeStringOnly() {
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x00, 0x05, 'h', 'e', 'l', 'l', 'o'});
    Object result = decoder.decode(ctx, buf);
    assertNotNull(result);
    // Bug in the alternative branch (type flag = 2) is never caught
}
```