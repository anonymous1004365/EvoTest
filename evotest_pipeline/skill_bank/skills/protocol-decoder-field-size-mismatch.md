---
name: protocol-decoder-field-size-mismatch
description: WHEN a protocol decoder reads fields from a binary buffer using methods
  like readUnsignedByte, readUnsignedShort, or readUnsignedInt, THEN verify that the
  correct byte-width method is used for each field. A mismatch (e.g., reading 2 bytes
  when the protocol specifies 1 byte) causes buffer misalignment, corrupting all subsequent
  field reads.
code_tags:
- BUFFER_OFFSET_HANDLING
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  - BUG_DETECTED
  transition_tags: []
  keywords:
  - readUnsignedByte
  - readUnsignedShort
  - field size mismatch
  - buffer misalignment
  - byte width
  - protocol decoder field read
---

WHEN a protocol decoder reads fields from a binary ByteBuf using methods like readUnsignedByte(), readUnsignedShort(), readUnsignedInt() in a loop or switch statement, THEN verify each field is read with the correct byte-width method by: (1) identifying all field-read calls in each decoding path, (2) checking that fields of the same semantic type use consistent byte widths across all paths, (3) testing with messages that exercise each field read to ensure the correct number of bytes is consumed, (4) verifying buffer reader index advances by the expected amount after each field read. Common pitfalls: using readUnsignedShort (2 bytes) where readUnsignedByte (1 byte) is correct, or vice versa.