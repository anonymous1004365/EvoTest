---
name: protocol-alternative-decoding-path
description: When a protocol decoder has multiple alternative decoding paths or branches, test that each path correctly handles valid messages without throwing unexpected exceptions. This skill applies when decoders use conditional logic (e.g., if-else, switch) to choose between different message format interpretations.
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK']
test_pattern: EXCEPTION_TEST
---

# protocol-alternative-decoding-path

## Instructions

# Protocol Alternative Decoding Path

## Instructions

- WHEN the TG encounters a protocol decoder class that uses conditional logic (e.g., `if`, `switch`, ternary) to select between alternative decoding paths based on message content (such as channel directives, frame markers, or message type bytes)
- THEN the TG MUST write tests that send messages exercising EACH alternative decoding branch, not just the primary or most common path
- Each test MUST assert that decoding completes without throwing an unexpected exception (e.g., `NullPointerException`, `ArrayIndexOutOfBoundsException`, `IllegalArgumentException`)
- WHEN the decoder uses a fixed-length frame, buffer, or byte array and an alternative path reads/writes to it
- THEN the TG MUST test boundary conditions such as minimum-length valid messages, messages with altered type bytes or markers, and messages that trigger each alternative path

**Common pitfalls:**
- Testing only the "happy path" of the primary decoding branch while ignoring alternative branches
- Assuming all messages have the same structure (e.g., expecting a certain field to always be present when an alternative branch may omit it)
- Using generic exception catching (e.g., `Exception`) instead of specific expected exceptions like `NullPointerException`
- Neglecting to verify that the decoder successfully returns a result (non-null) from each alternative path

**Example:**
```java
// CORRECT: Test each alternative decoding branch
@Test
public void testAlternativeDecodingPath() {
    // Primary path
    Object msg = decoder.decode(channel, remoteAddress, 
        BufferHelper.create("+HELLO"));
    assertNotNull(msg);
    
    // Alternative path (e.g., different message prefix)
    msg = decoder.decode(channel, remoteAddress, 
        BufferHelper.create("-WORLD"));
    assertNotNull(msg); // Would fail if alternative path throws NPE
}

// INCORRECT: Only testing the primary path
@Test
public void testOnlyPrimaryPath() {
    Object msg = decoder.decode(channel, remoteAddress, 
        BufferHelper.create("+HELLO"));
    assertNotNull(msg);
    // No test for alternative message formats - bug goes unnoticed
}
```