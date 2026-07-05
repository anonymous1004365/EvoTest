---
name: alternative-protocol-decoding-path
description: When a protocol decoder has an alternative decoding path that handles different message types or protocols, the TG must test that specific data intended for the primary decoder does not get passed to and break the alternative decoder path.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION', 'NULL_CHECK']
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class that contains multiple decoding paths or alternatives (e.g., checking for a specific message prefix, identifier, or pattern to decide which decoder to invoke)
- THEN the TG must test that data intended for one decoding path does not cause an exception or crash when passed to the alternative decoding path
- Include test cases with:
  - Data that hits the primary decoding path (e.g., messages with an expected prefix/identifier)
  - Data that hits the alternative decoding path (e.g., messages with a different prefix/identifier or format)
  - Data that might be ambiguous or boundary data between the two paths
- The test should verify that no uncaught exception is thrown for any valid data format, especially where the alternative path might attempt to parse fields that do not exist in the primary data format
- Common pitfalls:
  - Only testing one decoding path (usually the primary one) and missing that the alternative path crashes
  - Assuming that because data is "valid" for one path, it will be handled gracefully by the second path
  - Not testing with real-world protocol data that might be misrouted between decoders
  - Testing only with the exact format expected by the decoder, not with edge case variants

### Correct Example (for Pt502ProtocolDecoder style):
```java
// Correctly tests both decoding paths exist and handle their expected data
@Test
public void testDecode() throws Exception {
    // Create decoder with mock Channel/SocketAddress
    Pt502ProtocolDecoder decoder = new Pt502ProtocolDecoder(new Pt502Protocol());
    
    // Data for the primary decoding path
    String primaryData = "PT502,<some-data>";
    decoder.decode(null, null, primaryData);
    
    // Data for the alternative decoding path (different protocol/format)
    String altData = "OTHER,<data>";
    // Should not throw — test passes
    decoder.decode(null, null, altData);
}
```

### Incorrect Example:
```java
// BUG: Only tests one path, doesn't exercise the alternative path
@Test
public void testDecodePartial() throws Exception {
    Pt502ProtocolDecoder decoder = new Pt502ProtocolDecoder(new Pt502Protocol());
    
    // Only tests primary path
    String data = "PT502,<valid-data>";
    decoder.decode(null, null, data);
    // Missing: test the alternative decoding path which might crash
}
```