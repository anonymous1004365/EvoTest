---
name: protocol-decoder-endianness-mismatch-readIntLE
description: WHEN a protocol decoder bug involves switching from buf.readInt() (big-endian)
  to buf.readIntLE() (little-endian) for latitude/longitude or other multi-byte fields,
  THEN construct test data with little-endian byte order and verify that the buggy
  version reads the bytes as big-endian producing out-of-range or incorrect values,
  while the fixed version correctly interprets them as little-endian.
code_tags:
- ENDIANNESS
- BYTE_ORDER
- LITTLE_ENDIAN
- BIG_ENDIAN
- readIntLE
- PROTOCOL_DECODER_FRAME_HANDLING
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  - PASS_ON_BUGGY
  transition_tags:
  - ENDIANNESS_BUG
  - BYTE_ORDER_MISMATCH
  keywords:
  - readIntLE
  - readUnsignedIntLE
  - readShortLE
  - little-endian
  - big-endian
  - endianness
  - byte order
  - Latitude out of range
  - Iridium
  - decode04
  - Tramigo
  - Galileo
---

WHEN the diff shows a change from buf.readInt() to buf.readIntLE() (or readUnsignedInt to readUnsignedIntLE, readShort to readShortLE, etc.), identify the specific fields affected. Construct binary test data with the correct little-endian byte layout. On the buggy version, the same bytes will be interpreted as big-endian, producing values that may be out of range (e.g., latitude > 90). Use verifyPosition or verifyAttributes to check the decoded values. Also check for related skipBytes bugs where the length field includes header bytes.