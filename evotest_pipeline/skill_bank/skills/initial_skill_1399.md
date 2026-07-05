---
name: alternative-protocol-decoding-buffer-reuse
description: When a protocol frame decoder has an alternative decoding path that fails
  (e.g., buffer underflow), the decoder must restore position/state from before the
  alternative attempt. The skill teaches testing both the primary and alternative
  decoding paths, especially with malformed or incomplete data.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: STATE_TEST
---

# alternative-protocol-decoding-buffer-reuse

## Instructions

# Alternative Protocol Decoding — Buffer State Restoration

## Instructions

- WHEN the TG encounters a channel handler / protocol decoder class that attempts an "alternative" or "optional" decoding strategy (e.g., trying to decode from position 1 instead of position 0, or using a different data format) and this strategy may throw an exception or return null/empty
- THEN the TG must write a test that:
  1. Sends malformed or incomplete data that triggers the alternative decoding path AND causes that path to fail (e.g., buffer underflow)
  2. Verifies that after the failure, the next attempt to decode a well-formed message using the primary decoding path still succeeds — i.e., the buffer/channel state is fully restored
  3. The test should verify that no decoder state leak prevents correct message processing on subsequent calls
- Include concrete values: provide a byte sequence that triggers the alternative path (e.g., a header byte at index 0 that the decoder treats specially), then a subsequent valid byte sequence
- Common pitfalls:
  - Testing only one decoding path in isolation (either only the primary or only the alternative)
  - Assuming that if the alternative path throws, the buffer is automatically rewound by the framework — the decoder must handle rewind itself
  - Not resetting internal decoder state (e.g., `readerIndex` markers, `position` variables) before re-trying
  - Catching a "buffer underflow" exception without restoring the buffer's position to before the alternative attempt
- Example (correct): Send a byte array `[0x00, 0x01, ...]` where the decoder, seeing something at index 0, attempts an alternative parse, which fails; then send a valid packet that should have been decoded by the primary path — verify it decodes correctly
- Example (incorrect): Sending only the malformed data and confirming an exception is thrown (doesn't test state restoration), or sending only a valid message (doesn't test the impact of a failed alternative attempt)