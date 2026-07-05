---
name: protocol-message-parsing-null-safe
description: When parsing device protocol messages where indexed fields may be missing,
  ensure tests include both trimmed and un-trimmed messages as well as zero-length
  trailing fields, verifying that field accessors handle null or empty results without
  throwing.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# protocol-message-parsing-null-safe

## Instructions

# Protocol Message Parsing: Test Null-Safe Field Access

## Instructions

WHEN the Test Generator encounters a protocol decoder that parses message strings using indexed field splitting (e.g., `String.split(",")` followed by array access like `values[5].trim()` or `values[7]`), and the message format allows trailing fields to be absent, empty, or null:

- THEN the TG MUST write a test that supplies a message string with a trailing empty field (or fewer fields than accessed), causing `ArrayIndexOutOfBoundsException` or `NullPointerException` on the buggy version.
- THEN the TG MUST also test with a message that has the expected number of fields but with an empty trailing field (e.g., `"...0,0,,,,"` where trailing commas produce empty strings).
- THEN the TG MUST verify that the decoder does NOT throw any exception and correctly parses the available data when field access is done safely (fixed version).
- THEN the TG MUST assert that the decoder returns a non-null position object with at least valid (or default) values for the fields that were present.
- Common pitfalls: The TG might only test perfectly formatted messages with all fields present; this misses the bug entirely. The TG must also avoid testing only `null` input — the bug is about empty trailing fields in otherwise valid messages.
- Example of a good test:
```java
// Test with trailing empty field (buggy version throws ArrayIndexOutOfBoundsException)
Object result = decoder.decode(null, null, "123456789012345,,,080101,235960,,,,");
assertNotNull(result); // fixed version should handle gracefully
```

- Example of an **incorrect** test (does NOT catch this bug):
```java
// Only testing well-formed messages
Object result = decoder.decode(null, null, "123456789012345,10,50,080101,235960,A,10,20");
assertNotNull(result);
// Missing: empty trailing fields cause crash
```