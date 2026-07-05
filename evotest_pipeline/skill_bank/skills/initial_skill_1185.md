---
name: alternative-protocol-decoding-path
description: When a protocol frame decoder has an alternative/fallback decoding path that fails silently and returns inconsistent partial data, test should exercise both paths and ensure the combined output is correct.
code_tags: ['NULL_CHECK', 'BOUNDARY_CHECK', 'ARGUMENT_VALIDATION', 'ALTERNATIVE_PROTOCOL_DECODING', 'FRAME_DECODING_BOUNDARY', 'VALIDATION']
test_pattern: STATE_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

- WHEN the TG encounters a protocol frame decoder that has two or more alternative decoding paths (e.g., one path for certain frame types and another path for others), and a single call to the decoder processes multiple frames of different types in sequence:
  - THEN the TG should write a test that exercises both decoding paths within a single call, using mixed input that triggers both code branches.
  - The test should verify that the combined decoded result matches the expected output for all positions, not just for the first or last decoded entry.
  - Specifically, verify that every element in the decoded list/array has the correct type and non-default values. Do not assume that because one element decoded correctly, all elements did.
  - Verify that no exceptions or error messages are silently consumed during the alternative decoding path.

- Common pitfalls to avoid:
  - Testing only the primary decoding path while the bug lurks in the alternative path.
  - Testing only with homogeneous input (same frame type repeated) when the bug only manifests with mixed frame types.
  - Checking only the size/length of the result list without verifying the content of each individual decoded element.
  - Assuming that if the first element is correct, the rest are correct.
  - Failing to check that the last element(s) are non-null and have correct attribute values (the bug manifesting as null or zero-value fields in later elements).

- Example (correct):
  ```java
  // Mixed input where first frame triggers primary path, second frame triggers alternative path
  // Verify BOTH decoded positions have correct values
  List<Position> positions = decoder.decode(buf);  // buf contains 2 frames of different types
  assertEquals(2, positions.size());
  assertNotNull(positions.get(0));
  assertNotNull(positions.get(1));
  assertEquals(expectedValue1, positions.get(0).getAttribute(key));
  assertEquals(expectedValue2, positions.get(1).getAttribute(key));  // this line catches the bug
  ```

- Example (incorrect):
  ```java
  // Testing only homogeneous input (same frame type)
  List<Position> positions = decoder.decode(buf);  // only primary path frames
  assertEquals(2, positions.size());
  assertNotNull(positions.get(0));
  // Missing assertions for positions.get(1) — would not catch the alternative path bug
  ```