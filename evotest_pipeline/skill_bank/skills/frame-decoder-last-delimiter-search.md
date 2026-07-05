---
name: frame-decoder-last-delimiter-search
description: WHEN a protocol frame decoder uses buf.indexOf() or similar left-to-right
  search to find a frame delimiter byte, THEN test with input data where the delimiter
  character appears inside the payload data before the actual frame terminator. The
  bug occurs when the decoder finds the first occurrence instead of the last, causing
  premature frame truncation.
code_tags:
- FRAME_DECODING_BOUNDARY
- PROTOCOL_FRAME_DECODING
- BUFFER_OFFSET_HANDLING
- VALIDATION
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - FAIL_ON_FIXED
  transition_tags: []
  keywords:
  - indexOf
  - last occurrence
  - first occurrence
  - delimiter search
  - frame terminator
  - backwards scan
  - premature truncation
---

WHEN a protocol frame decoder searches for a delimiter byte (e.g., ']', '\n', 0x7E) using a left-to-right search method like buf.indexOf(fromIndex, toIndex, value), THEN check whether the decoder finds the first or the last occurrence. If it finds the first occurrence, test with input data where the delimiter character appears inside the payload before the actual frame terminator. Construct a test where: (1) the input buffer contains the delimiter as part of payload data, (2) the actual frame terminator is a later occurrence, (3) the expected output is the full frame including all data up to the last delimiter. On the buggy version (first-occurrence search), the decoder returns a truncated frame.