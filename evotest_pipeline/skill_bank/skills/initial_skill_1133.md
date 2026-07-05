---
name: alternative-protocol-decoding-null-handling
description: When a protocol decoder has multiple decoding paths (e.g., primary and
  alternative), test both paths including edge cases where alternative decoding path
  fails due to missing/null values. The TG should write tests that exercise alternative
  decoding logic with unexpected data.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- NULL_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decoding-null-handling

## Instructions

# Alternative Protocol Decoding with Null Handling

## Instructions

- WHEN the TG encounters a protocol frame decoder that has an alternative decoding path (e.g., a secondary `if` or `else if` block that processes data differently from the primary path), THEN the TG should write a test that specifically exercises that alternative path with edge case data.

- WHEN the alternative decoding path accesses methods on returned values (like `channel.toString()`, `msg.toString()`, or similar chained method calls) without null checking, THEN the TG should test that path with a null or unexpected argument that would cause the alternative path to fail (e.g., a NullPointerException).

- WHEN a decoder class has methods that return decoded frames (like `decode()` returning an `Object`), THEN the TG should verify the behavior when the alternative decoding branch is triggered with data that causes the branch to throw an unhandled exception on the buggy version while succeeding on the fixed version.

- Common pitfall: Testing only the primary/successful decoding path while ignoring the alternative fallback path where null-checking logic was added in the fix.

- Example (correct for catching the bug):
```java
@Test
public void testDecodeAlternativePathWithNullMsg() {
    ThinkRaceProtocolDecoder decoder = new ThinkRaceProtocolDecoder();
    Channel channel = mock(Channel.class);
    SocketAddress remoteAddress = mock(SocketAddress.class);
    
    // Call decode with data that triggers the alternative decoding path
    // On buggy version this throws NPE, on fixed version it handles gracefully
    assertThrows(NullPointerException.class, () -> {
        decoder.decode(channel, remoteAddress, someDataThatTriggersAlternativePath);
    });
}
```

- Example (incorrect — does not catch the bug):
```java
@Test
public void testDecodePrimaryPath() {
    ThinkRaceProtocolDecoder decoder = new ThinkRaceProtocolDecoder();
    // Only tests the happy path, never triggers the alternative branch
    Object result = decoder.decode(channel, remoteAddress, validData);
    assertNotNull(result);
}
```