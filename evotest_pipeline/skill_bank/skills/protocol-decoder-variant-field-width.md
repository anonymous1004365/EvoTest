---
name: protocol-decoder-variant-field-width
description: WHEN a protocol decoder detects a device variant (e.g., via header bytes,
  length fields, or marker values) and changes the byte-width of subsequent field
  reads (e.g., speed as 1 byte vs 2 bytes), THEN write a test that crafts a message
  triggering the variant detection and verifies each field is read with the correct
  byte-width. The test must verify that buffer alignment is maintained and all decoded
  fields have correct values.
code_tags:
- VARIANT_DETECTION
- ALTERNATIVE_DECODING_PATH
- BUFFER_OFFSET_HANDLING
- PROTOCOL_MESSAGE_TYPE_SWITCH
test_pattern: PARAMETRIC_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - PASS_FAIL
  transition_tags:
  - VARIANT_DETECTION
  - ALTERNATIVE_DECODING_PATH
  keywords:
  - variant
  - decodeVariant
  - field size
  - readUnsignedByte
  - readUnsignedShort
  - buffer alignment
  - alternative path
---

WHEN the TG encounters a protocol decoder with a decodeVariant or similar method that sets an internal variant field based on header/length/marker bytes, and the variant changes how fields are read (e.g., readUnsignedByte vs readUnsignedShort for speed), THEN: (1) Identify the exact byte pattern that triggers each variant. (2) Craft a binary message with that pattern. (3) Verify that fields read with variant-dependent widths produce correct values. (4) Verify that buffer reader index advances by the expected total bytes. (5) Test both the variant path and the standard path to ensure consistency.