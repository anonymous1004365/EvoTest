---
name: alternative-protocol-frame-decoder
description: A protocol message decoder has multiple decoding paths (e.g., JSON and
  binary) but the alternative path fails to properly parse or decode messages, leading
  to an IllegalArgumentException. Apply this skill when testing multi-format protocol
  decoders to ensure both primary and alternative decoding paths work correctly.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-frame-decoder

## Instructions

# Alternative Protocol Frame Decoder Test Skill

## Instructions

**WHEN** the TG encounters a protocol message decoder that supports multiple message formats (e.g., both JSON messages and binary/hexadecimal frames), and the decoder has conditional logic to select between decoding paths (e.g. an `if-else` chain that checks for `"s"` parameter or provides a fallback):

- **THEN** the TG should write a parametric test that exercises **each distinct decoding path** with a representative sample of valid input data for that path.
- **Concretely**, if the primary path expects a JSON message parameter (e.g., request containing `"s"` field), and the alternative path handles a binary/hex payload (e.g., passing `"<hex>"` to a method that parses it as raw bytes), the TG must:
  1. Create at least one test case that exercises the **primary/JSON path** (e.g., `"s=someJsonPayload..."`)
  2. Create at least one test case that exercises the **alternative/binary path** (e.g., `"<hexadecimal_string>"`)
- **For the alternative path**, the test should verify no exception is thrown and the decoding produces a meaningful result. On the buggy version, the alternative path may throw an `IllegalArgumentException` due to incorrect parsing logic (e.g., failing to handle the hex string format, reaching an invalid position in the input, or misinterpreting the decoded data).
- **Common pitfalls to avoid:**
  - Testing only the primary/JSON path, assuming that's the only format the decoder handles.
  - Assuming that if one decoding path works, all paths work correctly.
  - Testing with incomplete or overly simplistic payloads that don't exercise the full decoding logic (e.g., payloads that are too short or lack necessary framing elements like length prefixes).
  - Forgetting that the alternative path may rely on a different data structure (e.g., raw bytes vs. key-value pairs).

### Concrete Example (Correct)

```java
@Test
public void testDecode() throws Exception {
    DmtHttpProtocolDecoder decoder = new DmtHttpProtocolDecoder(null);
    
    // Primary/JSON path test
    String jsonPayload = "s={\"t\":1,\"ts\":999,\"d\":\"...\"}";
    assertNotNull(decoder.decode(null, null, jsonPayload));
    
    // Alternative/binary hex path test — this is what was buggy
    String hexPayload = "<hex_string_with_length_prefix>";
    assertNotNull(decoder.decode(null, null, hexPayload));
}
```

### Concrete Example (Incorrect — Missing Alternative Path)

```java
@Test
public void testDecode() throws Exception {
    DmtHttpProtocolDecoder decoder = new DmtHttpProtocolDecoder(null);
    
    // Only tests the JSON path — incomplete!
    String jsonPayload = "s={\"t\":1,\"ts\":999,\"d\":\"...\"}";
    assertNotNull(decoder.decode(null, null, jsonPayload));
    
    // Missing: no test for the binary/hex decoding path
}
```