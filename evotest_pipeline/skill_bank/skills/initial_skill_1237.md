---
name: alternative-decoding-path-null-safety
description: When a protocol decoder checks for multiple message formats and has an
  alternative decoding path that can return null while executing nested field access
  on that null, write tests that exercise the alternative branch to catch NullPointerException.
code_tags:
- NULL_CHECK
- VALIDATION
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# alternative-decoding-path-null-safety

## Instructions

# Alternative Decoding Path Null Safety

## Instructions

- WHEN the TG encounters a protocol decoder that checks for different message formats (e.g., checking `msgType` or having `if-else` branches for different channel buffer frame formats)
- THEN the TG should write tests that force execution through **each alternative decoding path**, not just the primary or most common one
- WHEN testing an alternative decoding path, verify that the decoder handles cases where the initial parsing returns `null` (e.g., a method like `decode` returns `null` on one branch while subsequent code accesses fields on the result without null-checking)
- THEN the test should provide input data that triggers the alternative branch and expect a `NullPointerException` on the buggy version
- The test should construct channel buffers with specific data patterns (e.g., device identifiers, message types) that are recognizable by the decoder's branching logic
- **Common pitfalls to avoid:**
  - Testing only the happy path where the primary decoding format succeeds
  - Assuming the decoder always returns a non-null result from the `decode` method
  - Not constructing buffer data with the correct frame structure to trigger the alternative branch
  - Hard-coding expected decoded values without considering that the alternative path may not produce a valid result
  - Using generic buffer contents that don't match any recognizable protocol format

**Example (correct):** The test should construct a channel buffer with data that matches the alternative protocol format, invoke the decoder, and assert on the exception:

```java
// Example: Triggering the alternative decoding path with data that causes null return
ByteBuf buf = Unpooled.buffer();
buf.writeByte(0x00); // some header indicating alternative format
buf.writeBytes(...);  // payload matching alternative decoder logic
assertThrows(NullPointerException.class, () -> decoder.decode(channel, null, buf));
```

**Example (incorrect):** Only testing the primary decoding path with valid data:

```java
// WRONG: Only tests the primary path, misses the null issue on alternative path
ByteBuf buf = Unpooled.buffer();
buf.writeBytes(primaryFormatData);
assertNotNull(decoder.decode(channel, null, buf));
```