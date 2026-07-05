---
name: alternative-protocol-decoding-path
description: When a protocol frame decoder has two or more parsing paths (e.g., primary buffer-based and alternative position-based paths), tests must cover both. The alternative path may incorrectly preserve or fail to initialize critical state (e.g., non-primitive data fields), causing NPEs or decoding failures.
code_tags: ['ARGUMENT_VALIDATION', 'STATE_MUTATION', 'ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: STATE_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

- WHEN the TG encounters a protocol frame decoder class (e.g., `TmgProtocolDecoder`, `MyProtocolDecoder`) that has a primary decoding path (often buffer-based) AND an alternative decoding path (e.g., triggered by a position flag or data field), AND the alternative path preserves or re-uses state from the primary path (e.g., a non-primitive field like `Long`, `String`, or a custom object instance)
- THEN the TG MUST create a test that sends data designed to trigger the **alternative path only** and verifies that all data fields are correctly populated, including fields that the primary path would normally set. The test should call the decode method (or its helper methods) with the alternative path and assert that no NullPointerException occurs and that expected values are correctly decoded.

- Include concrete values from the actual protocol: use the exact data bytes/hex strings, exact field names, and exact exception class (e.g., `NullPointerException`, `IllegalArgumentException`, or a specific protocol exception).

- Common pitfalls to avoid:
  - Testing only the primary/default decoding path (e.g., only sending standard frames without the alternative flag).
  - Assuming that fields set by the primary path will be non-null when accessed from the alternative path.
  - Not testing with boundary/edge-case values for the alternative path trigger (e.g., the minimum/maximum allowed position flag).
  - Forgetting to verify every non-primitive field that the decoder exposes after both paths complete.

### Correct Example (Java/JUnit)

```java
@Test
public void testDecodeAlternativePath() throws Exception {
    // Arrange: build a byte buffer that triggers the ALTERNATIVE decoding path
    // (e.g., including a position field with a specific non‑zero flag)
    byte[] data = new byte[] {
        0x00, 0x01, 0x02, 0x03, // header / some prefix
        0x01,                   // position flag → alternative path
        0x00, 0x00, 0x00, 0x0A  // data payload
    };
    
    TmgProtocolDecoder decoder = new TmgProtocolDecoder();
    
    // Act
    Object result = decoder.decode(null, null, Unpooled.wrappedBuffer(data));
    
    // Assert: all non‑primitive fields must be non‑null
    assertNotNull(result);
    // If the decoded object has a 'timestamp' field (Long), check it is not null
    assertNotNull("Timestamp should not be null on alternative path", 
                   ((MyPosition) result).getTimestamp());
    // Verify the decoded value is correct
    assertEquals(10, ((MyPosition) result).getValue());
}
```

### Incorrect Example (what NOT to do)

```java
@Test
public void testDecodeOnlyPrimaryPath() throws Exception {
    // BUG: Only tests the primary path (position flag = 0)
    byte[] data = new byte[] {
        0x00, 0x01, 0x02, 0x03,
        0x00,                   // position flag → primary path only
        0x00, 0x00, 0x00, 0x0A
    };
    
    TmgProtocolDecoder decoder = new TmgProtocolDecoder();
    Object result = decoder.decode(null, null, Unpooled.wrappedBuffer(data));
    
    // This test passes on buggy code because the primary path works fine.
    // The alternative path (position flag = 1) remains untested.
    assertNotNull(result);
}
```