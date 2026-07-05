---
name: protocol-decoder-alternative-parse-path
description: When testing protocol decoders that offer multiple parsing paths (e.g.,
  trying one format, then falling back to another), ensure tests cover both paths
  — especially the alternative/fallback path that may have independent defects. The
  primary path may work while the secondary path fails silently.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# protocol-decoder-alternative-parse-path

## Instructions

# Protocol Decoder — Test All Alternative Parsing Paths

## Instructions

- WHEN the TG encounters a protocol decoder class that attempts parsing with one scheme (e.g., `ProtocolUtil.parseProtocol`, `decode`, `readString`, etc.), and upon failure (e.g., catching an `Exception`, checking for `null`, or checking `remaining()` bytes) falls back to an **alternative decoding strategy**
- THEN the TG **must write a test that specifically covers the alternative/fallback decoding path**, not just the primary path:
  - Construct a valid input that triggers the **alternative path** (e.g., a message that would cause the primary parse to fail/return null, but is valid for the alternate parser)
  - Verify that the decoded result is **correct** (expected device ID, position, timestamp, etc.)
  - Verify that the alternative path does **not throw an unexpected exception** (e.g., `StringIndexOutOfBoundsException`, `ArrayIndexOutOfBoundsException`, `NullPointerException`)
- **Common pitfalls:**
  - Testing only the "happy path" where the primary parser succeeds, missing defects hidden in the fallback logic
  - Assuming that because the primary fallback checks for `null` or `false`, the alternative path is safe
  - Forgetting to test edge cases of the alternative parser (e.g., message length shorter than expected, missing delimiters, empty fields)
  - Using test data that happens to work in both paths, making it unclear which path is actually being exercised
- **Example (correct):** Given a protocol decoder that first tries parsing with a `bit_buffer` / `readSigned` approach and upon failure falls back to `string.split(",")` + numeric parsing, the test should include a message like `"135790246892201,20151010110203,1,3,10.0,20.0,30.0,40.0,50,1,2,3"` (a comma-separated format that fails the bit-encoded protocol, but should succeed in the fallback). Verify the decoded position has `latitude=10.0`, `longitude=20.0`, and no exception.
- **Example (incorrect):** Only testing with binary/bit-encoded protocol messages (e.g., hex `"080800..."`) that exercise the primary path, and never testing with comma-separated text messages that exercise the fallback, leaving the fallback path untested.