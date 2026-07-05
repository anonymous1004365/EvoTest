---
name: structured-data-key-length-validation
description: When working with StructuredDataMessage in Log4j, map keys that exceed
  the RFC 5424 maximum key length of 32 characters must be rejected with an IllegalArgumentException.
  This skill teaches the TG to write tests that verify key length validation, catching
  cases where overly long keys silently cause data integrity issues.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# structured-data-key-length-validation

## Instructions

# Structured Data Key Length Validation

## Instructions

- WHEN the TG encounters `StructuredDataMessage` or `StructuredDataId` classes that allow inserting key-value pairs via methods like `put(String key, String value)`
- THEN it should test that inserting a key longer than 32 characters throws an `IllegalArgumentException`
- The maximum key length for structured data elements in RFC 5424 is 32 characters (SD-ID length limit)
- Verify that keys of exactly 32 characters are accepted (boundary case), and keys of 33+ characters are rejected
- Use `assertThrows(IllegalArgumentException.class, () -> ...)` to assert the exception

### Common pitfalls to avoid
- **Testing only String values**: Make sure to validate the key, not just the value. The bug is in key length validation, not value validation.
- **Forgetting boundary testing**: Test both sides of the boundary — valid (32 chars) and invalid (33 chars).
- **Testing with wrong exception type**: The expected exception is `IllegalArgumentException`, not `RuntimeException` or another generic type.
- **Testing a different method**: The key validation applies to `put(String key, String value)` and similar methods that accept a key parameter in `StructuredDataMessage`.

### Example (correct)
```java
@Test
public void testMsgWithKeyTooLong() {
    assertThrows(IllegalArgumentException.class, () -> {
        final StructuredDataMessage msg = new StructuredDataMessage("TestId", "TestMsg", "TestType");
        msg.put("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567", "TestValue");  // 33 chars
    });
}
```

### Example (incorrect — missing the assertion)
```java
@Test
public void testMsgWithKeyTooLong() {
    StructuredDataMessage msg = new StructuredDataMessage("TestId", "TestMsg", "TestType");
    msg.put("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567", "TestValue");  // No assertion — won't verify the exception
}
```

### Example (incorrect — testing value instead of key)
```java
@Test
public void testMsgWithValueTooLong() {
    StructuredDataMessage msg = new StructuredDataMessage("TestId", "TestMsg", "TestType");
    msg.put("Key", "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567");  // Values can be any length; no exception thrown
}
```