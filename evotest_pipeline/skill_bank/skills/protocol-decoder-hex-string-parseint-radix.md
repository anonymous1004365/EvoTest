---
name: protocol-decoder-hex-string-parseint-radix
description: WHEN a protocol decoder uses ByteBufUtil.hexDump() to convert a buffer
  slice to a hex string and then parses it with Integer.parseInt(value), THEN the
  TG must verify that Integer.parseInt(value, 16) is used (hex radix) instead of Integer.parseInt(value)
  (decimal radix). The bug causes NumberFormatException when hex digits A-F appear
  in the value. Test with ADC values, sensor readings, or any hex-encoded numeric
  fields that contain hex digits a-f.
code_tags:
- HEX_PARSING
- RADIX_BUG
- TYPE_CONVERSION
- EXCEPTION_HANDLING
- PROTOCOL_DECODER_FRAME_HANDLING
test_pattern: EXCEPTION_TEST
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
  - HEX_PARSING
  - RADIX
  keywords:
  - hexDump
  - parseInt
  - radix
  - hex string
  - ADC
  - ByteBufUtil
  - NumberFormatException
---

WHEN the TG encounters a protocol decoder that reads a 2-byte slice via buf.readSlice(2), converts it to hex via ByteBufUtil.hexDump(), and parses it with Integer.parseInt(value), THEN the TG should: 1) Identify the specific line where Integer.parseInt(value) is called on a hex string, 2) Create a test message where the hex-encoded field contains digits A-F (e.g., '0a', '1f', 'a0'), 3) Verify that on the buggy version the test throws NumberFormatException, and on the fixed version it correctly parses the value. Use EXCEPTION_TEST pattern with assertThrows for the buggy version.