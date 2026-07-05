---
name: protocol-decoder-timestamp-handling
description: When a protocol decoder has an alternative decoding path that uses a
  different timestamp resolution (seconds vs milliseconds), test both paths to ensure
  consistent timestamp semantics. Use this skill when the decoder handles incomplete
  position data with timestamp conversions.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: STATE_TEST
---

# protocol-decoder-timestamp-handling

## Instructions

# Protocol Decoder Timestamp Handling

## Instructions

- WHEN the TG encounters a protocol decoder that has two or more decoding paths (e.g., a default path and an alternative/fallback path triggered by missing data, incomplete attributes, or device-specific flags)
- THEN the TG should test ALL decoding paths end-to-end, not just the primary path, by constructing device data that triggers the alternative path
- Verify that the decoded position's timestamp is handled consistently across paths — particularly whether timestamps are interpreted as seconds vs milliseconds
- WHEN the alternative path converts timestamps (e.g., multiplies by 1000 to convert seconds to milliseconds), verify this conversion is actually applied. A missing conversion on one path while another path has it leads to timestamp values that are off by a factor of 1000 (epoch timestamps in seconds not converted to milliseconds)
- Include concrete tests with known epoch timestamp values (e.g., a date like 2016-01-25T15:24:18Z) and assert the expected decoded time
- Common pitfalls:
  - Only testing the primary/complete-data path while ignoring error recovery or fallback paths
  - Assuming timestamp handling is identical across all code paths without verifying
  - Testing with relative timestamps/offsets instead of concrete epoch values that expose scaling errors

### Correct Example (triggering test pattern)

```java
// Test both the regular and alternative decoding paths
// The buggy version failed to convert timestamps in the alternative path (seconds to ms)

// Test with data that triggers the fallback path (missing precision attribute)
// Verify the decoded timestamp matches expected epoch in milliseconds
Position position = decoder.decode(null, null, ByteBufUtil.hexDump("some_hex_payload"));
assertNotNull(position);
// If the time is 2016-01-25 15:24:18 UTC = 1453735458 seconds, expect 1453735458000 ms
assertEquals(1453735458000L, position.getFixTime().getTime());
```

### Incorrect Example

```java
// Only testing the primary/most-common code path
// Does NOT catch the alternative path timestamp bug
Position position = decoder.decode(null, null, ByteBufUtil.hexDump("primary_path_payload"));
assertNotNull(position);
// Missing: test with data that triggers the fallback path where timestamp scaling is broken
```