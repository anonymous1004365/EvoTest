---
name: alternative-protocol-decoding-path
description: When a protocol decoder has an alternative/fallback decoding path that can fail silently without throwing or logging an error, write a test that exercises both the primary and alternative decoding paths and verifies that the alternative path produces a correctly decoded result (not null/empty).
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding — Test Both Primary and Fallback Paths

## Instructions

- WHEN the Test Generator (TG) encounters a protocol frame decoder that has an `instanceof` check or type-matching condition (e.g., `if (buf instanceof ByteBuf) { ... } else { ... }`) where the `else` branch (alternative/fallback path) processes the message differently
- THEN the TG MUST write a parametric test that exercises **BOTH** the primary and the alternative decoding paths using different types of input buffers/messages, verifying that both paths produce non-null, correctly decoded results
  - For the primary path: provide input that matches the first condition (e.g., `ByteBuf`-compatible message)
  - For the alternative path: provide input that falls through to the `else` branch (e.g., a plain `String` or `ChannelBuffer` of a different type)
  - Verify that the decoded result from both paths is non-null and has the expected structure (e.g., contains a position field, has identifiers parsed, etc.)
- Include concrete values/types/examples from the actual code:
  - If the decoder has `if (buf instanceof ByteBuf)` then `else` for `String` or other types, test with both a `ByteBuf` message and a `String` message that contains the same data
- What the test should verify on the buggy version: The alternative path produces `null`, a zero-length result, or throws an unexpected exception (like `StringIndexOutOfBoundsException`, `IndexOutOfBoundsException`, or `ClassCastException`)
- What the test should verify on the fixed version: Both paths produce a complete, correctly decoded object with all expected fields populated

### Common pitfalls to avoid
- **Testing only the primary decoding path** — This is the most common mistake. When you see an `if/else` or type-switch in a decoder, you MUST test both branches.
- **Assuming the alternative path works because the primary path works** — The bug is specifically that the alternative path is broken.
- **Not verifying the decoded object fields** — Simply checking that the method doesn't throw is insufficient; verify that the decoded result contains expected data (e.g., position, identifiers, message type).
- **Testing only one input type** — The decoder handles multiple message formats; test each format.

### Example

**Correct approach:**
```java
@Test
public void testDecodeAlternativePath() {
    AisProtocolDecoder decoder = new AisProtocolDecoder();
    // Alternative path (e.g., String input — the broken path)
    String msg = "!AIVDM,1,1,,A,13P`0D001d0MdM7NF0Di`m=<5pPp,0*69";
    Object result = decoder.decode(null, null, msg);
    assertNotNull("Alternative path should decode String messages", result);
    // Verify the decoded position is present (not default/empty)
    Position position = (Position) result;
    assertNotNull(position.getLatitude());
    assertNotNull(position.getLongitude());
}

@Test
public void testDecodePrimaryPath() {
    AisProtocolDecoder decoder = new AisProtocolDecoder();
    // Primary path (e.g., ByteBuf input)
    ByteBuf buf = Unpooled.copiedBuffer("!AIVDM,1,1,,A,13P`0D001d0MdM7NF0Di`m=<5pPp,0*69", Charset.UTF_8);
    Object result = decoder.decode(null, null, buf);
    assertNotNull("Primary path should decode ByteBuf messages", result);
}
```

**Incorrect approach:**
```java
// BAD: Only tests one path, doesn't cover the alternative decoding path
@Test
public void testDecode() {
    AisProtocolDecoder decoder = new AisProtocolDecoder();
    ByteBuf buf = Unpooled.copiedBuffer("!AIVDM,...", Charset.UTF_8);
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // Missing: test with String input
}
```