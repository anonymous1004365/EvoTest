---
name: protocol-decoder-alternative-path-validation
description: When a protocol frame decoder has an alternative decoding path that processes
  data differently from the main path, tests must verify both paths handle valid,
  malformed, and edge-case inputs correctly. This skill prevents bugs where the alternative
  path misses null checks or validation.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-path-validation

## Instructions

# Protocol Decoder Alternative Path Validation

## Instructions

1. **WHEN** a protocol decoder class (e.g., `GnxProtocolDecoder`) contains an alternative decoding path (e.g., a conditional branch based on message type, length, or format flag) that processes frame data differently from the main decoding path:
   - **THEN** the test should provide input data that exercises each alternative branch independently
   - **AND** verify that each branch returns a correctly decoded position or protocol message without throwing `NullPointerException` or `IndexOutOfBoundsException`
   - **AND** include test inputs where parameters or fields accessed in the alternative path may be `null`, empty, or incomplete

2. **WHEN** the alternative decoding path accesses sub-fields, nested objects, or optional attributes of a decoded message (e.g., extracting position data from a protocol-specific sub-packet):
   - **THEN** test with inputs where those sub-fields are present (valid) AND absent (null/missing)
   - **AND** assert that a missing optional sub-field does not cause a crash but returns the partial result gracefully or skips the field

3. **WHEN** constructing test protocol messages that contain multiple data fields in a binary format:
   - **THEN** use realistic hex-encoded byte arrays for the protocol messages, with variant formats that exercise both the main and alternative decoding paths
   - **AND** include at least one test case with a `null` or empty payload to verify defensive handling

4. **Common pitfalls to avoid:**
   - ❌ Testing only the "happy path" (main decoding branch) and ignoring the alternative path
   - ❌ Providing input where all optional attributes are always present, masking null-safety issues in the alternative branch
   - ❌ Only testing non-null data — the alternative branch may fail when data is incomplete or malformed
   - ❌ Assuming the protocol decoder always gets well-formed messages — test with corrupted/missing fields

### Example (correct approach):
```java
// Test both the main and alternative decoding paths
// Main path: standard protocol message
byte[] mainPathMsg = { /* hex bytes for standard format */ };
Position mainResult = decoder.decode(null, null, mainPathMsg);
assertNotNull(mainResult);

// Alternative path: variant format with optional fields
byte[] altPathMsg = { /* hex bytes for alternative format */ };
Position altResult = decoder.decode(null, null, altPathMsg);
assertNotNull(altResult);

// Edge case: incomplete data in alternative path
byte[] incompleteMsg = { /* hex bytes missing optional field */ };
Position incompleteResult = decoder.decode(null, null, incompleteMsg);
// Should not throw NPE — may return null or partial position
assertNotNull(incompleteResult); // or appropriate assertion
```

### Example (incorrect approach — masking the bug):
```java
// Only testing main path
byte[] msg = { /* hex bytes for standard format only */ };
Position result = decoder.decode(null, null, msg);
assertNotNull(result);

// Missing: alternative format test
// Missing: incomplete/malformed data test
// Missing: null payload test
```