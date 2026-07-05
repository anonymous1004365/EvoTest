---
name: alternative-protocol-decoding-path
description: When a protocol decoder has alternative parsing paths (e.g., fallback to a different format when primary parsing fails), TG should test both paths explicitly with malformed or incomplete data to ensure the alternative path correctly handles edge cases like missing fields or null returns.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

- WHEN the TG encounters a protocol decoder class that has alternative/fallback decoding logic (e.g., an `else` branch, a `catch` block that falls through to a secondary parser, or a conditional that chooses between two different message parsing strategies based on content type or field presence)
- THEN the TG should write a parametric test that covers both the primary AND the alternative decoding path with the following concretely: (1) a valid message that exercises the primary path, (2) a malformed or incomplete message that forces the alternative path, (3) edge cases where fields expected by the alternative path might be null, empty, or missing
- The TG should verify that the alternative decoding path does NOT throw unexpected exceptions (like NullPointerException or IndexOutOfBoundsException) and produces a correctly decoded result (or at minimum, does not crash)
- Common pitfalls to avoid: (a) testing only the primary/standard decoding path and assuming the alternative path works identically; (b) forgetting that the alternative path may access different fields, indices, or perform different type conversions than the primary path; (c) providing only well-formed test data that never triggers the alternative path; (d) not testing edge cases where alternative path fields are null, empty, or malformed

### Correct Example (in pseudocode style)

```java
@Test
public void testDecodeAlternativePath() {
    ProgressProtocolDecoder decoder = new ProgressProtocolDecoder();
    
    // Primary path: well-formed message
    Object result1 = decoder.decode(null, null, new ChannelBuffer("..."));
    assertNotNull(result1);
    
    // Alternative path: malformed message (e.g., missing key field, wrong delimiter)
    // This should NOT throw NullPointerException on the alternative path
    Object result2 = decoder.decode(null, null, new ChannelBuffer("incomplete|data"));
    // Assert that result2 is either null or a valid decoded object
    // but NOT an exception
    assertNotNull(result2);
}
```

### Incorrect Example (pitfall to avoid)

```java
@Test
public void testDecodeOnlyPrimaryPath() {
    // ❌ Only tests the happy/primary path
    ProgressProtocolDecoder decoder = new ProgressProtocolDecoder();
    Object result = decoder.decode(null, null, new ChannelBuffer("valid|message|data|here"));
    assertNotNull(result);
    // The alternative path is never exercised
    // If a bug exists only on the alternative path, this test won't catch it
}
```