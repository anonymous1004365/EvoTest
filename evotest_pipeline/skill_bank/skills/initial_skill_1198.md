---
name: protocol-decoder-fallback-failure
description: When a protocol decoder has alternative decoding paths, test each path's
  edge cases including malformed input to ensure no RuntimeException escapes unhandled
  and the decoder can gracefully recover.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-fallback-failure

## Instructions

# Protocol Decoder Fallback Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses a try-catch fallback pattern (e.g., attempting one decoding strategy and catching an exception to try an alternative), THEN the TG should write a test that feeds the decoder deliberately malformed or incomplete messages that trigger the primary path to throw, verifying that the fallback path:
  1. Does not itself throw any unexpected RuntimeException
  2. Returns a valid result (even if it's a default/empty result) rather than letting the exception propagate

- WHEN the TG encounters a decoder that tries multiple parsing strategies and catches generic Exceptions (e.g., `catch (Exception e)` or `catch (RuntimeException e)`), THEN the TG should specifically test edge cases like:
  - Empty byte arrays or buffers
  - Data that partially matches one format but is ultimately invalid
  - Messages with correct framing but corrupted payload content
  - Verify the decoded result is non-null and has sensible default values

- Common pitfalls to avoid:
  - Testing only happy-path valid messages — the bug usually lives on a secondary path
  - Assuming that because an exception is caught, the fallback always works — test the fallback specifically
  - Testing with only one type of malformed message — test several variants (truncated, extra bytes, wrong encoding, corrupted fields)

- Example (correct): When testing `MiniFinderProtocolDecoder.decode()` with a malformed message that triggers the primary parsing to throw a `StringIndexOutOfBoundsException`, the test should ensure the decoder catches this and returns a valid position object (e.g., with default coordinates) rather than throwing.

- Example (incorrect): Only testing well-formed protocol messages of one format type, leaving the fallback parsing path untested.