---
name: alternative-phone-decode-fallback
description: Detects bugs where a protocol decoder's primary decode path throws an
  exception and falls back to an alternative path that may have different parsing
  logic, leading to incomplete or corrupted data.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_ITERATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# alternative-phone-decode-fallback

## Instructions

# Alternative Decode Path for Phone Protocols

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `XexunProtocolDecoder`) that has multiple decode methods (e.g., `decode` with different parameter types like `Channel` vs no channel, or `Object` vs `String`) or catches exceptions (e.g., `try { ... } catch (Exception e) { ... }`) to fall back to an alternative parsing path
- THEN the TG should write a parametric test that provides input data valid for the **primary** decode path but that triggers an exception or mismatch in that path, forcing execution into the secondary/fallback path. The test should verify that the fallback path still produces a valid decoded object and does NOT silently lose data or return null/malformed results.
- WHEN the secondary decode path does not handle all fields or does not fill in device-specific metadata (e.g., phone number, IMEI, protocol version)
- THEN the test should **assert that specific fields present in the input are present in the decoded output**, not just that decoding does not throw.
- Common pitfalls to avoid: 
  - Testing only the happy path (primary decode succeeds) and ignoring the fallback path
  - Assuming the fallback path is equivalent to the primary path
  - Testing only that no exception is thrown, without verifying actual output values (e.g., phone number, IMEI, position)
  - Testing with malformed input that would fail both paths, masking the bug
  - Not including at least one **valid** input that exercises the fallback path and yields correct output values

### Correct Example (checks fallback path output)
```java
@Test
public void testDecodeWithFallbackPath() throws Exception {
    XexunProtocolDecoder decoder = new XexunProtocolDecoder(null);
    // Input that triggers exception in primary path, forcing fallback
    String input = "...";
    Object result = decoder.decode(null, null, input);
    assertNotNull("Fallback decode returned null", result);
    // Verify key fields are present
    assertTrue("Phone number missing", result.toString().contains("12345"));
}
```

### Incorrect Example (missing fallback path coverage)
```java
@Test
public void testDecodeHappyPath() throws Exception {
    XexunProtocolDecoder decoder = new XexunProtocolDecoder(null);
    String input = "...";
    Object result = decoder.decode(null, null, input);
    assertNotNull(result);
    // No testing of fallback path - this would miss the bug!
}
```