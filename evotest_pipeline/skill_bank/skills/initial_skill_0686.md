---
name: form-parameter-inclusion-check
description: WHEN a HTTP request builder class (e.g., StartResumeUsersPlaybackRequest)
  uses `setBodyParameter` or `setFormParameter` to set parameters, THEN the test should
  verify that the built request actually includes all expected parameters (e.g., position_ms)
  by checking the request's serialized/form output. Without this check, a bug where
  the builder silently omits a parameter during request construction may go undetected.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- FORM_PARAMETER_VALIDATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# form-parameter-inclusion-check

## Instructions

# Form Parameter Inclusion Check

## Instructions

- WHEN the TG encounters a request builder class that uses `setBodyParameter(key, value)` or `setFormParameter(key, value)` methods to populate HTTP request parameters (e.g., `position_ms` with value `10000`),
- THEN the TG should write a test that:
  1. Constructs a request using the builder, providing all mandatory parameters (including non-null values).
  2. Inspects the built request's serialized form (e.g., `request.getBody()` or `request.toString()` or the form parameter map) to verify that every expected parameter key and value is present.
  3. Specifically, the test should verify that the parameter `position_ms` is present and equals the expected value (e.g., `"10000"`), not only that no exception is thrown during construction.

- Common pitfalls to avoid:
  1. **Testing only construction, not content**: The TG might test that `builder.setFoo(x).build()` succeeds without checking that `foo=x` survived into the request body. This misses bugs where parameters are silently lost.
  2. **Testing serialization only for one parameter type**: If the bug only affects a specific parameter (e.g., `position_ms`), testing only with String parameters may pass while the bug remains for other types.
  3. **Assuming default values appear**: Do not assume that parameter defaults or absent values will appear in the request output — explicitly set and verify each parameter.

### Correct Example (what the test should do):
```java
@Test
public void shouldComplyWithReference() {
  StartResumeUsersPlaybackRequest request = new StartResumeUsersPlaybackRequest.Builder()
      .setPositionMs(10000)
      .build();
  
  String body = request.getBody();
  // Verify the parameter is actually present in the serialized request
  assertTrue("position_ms should be in request body", body.contains("position_ms"));
  assertTrue("position_ms value 10000 should be in request body", body.contains("10000"));
}
```

### Incorrect Example (what misses the bug):
```java
@Test
public void shouldNotThrow() {
  // This only tests that the builder doesn't throw, NOT that the parameter is included
  StartResumeUsersPlaybackRequest request = new StartResumeUsersPlaybackRequest.Builder()
      .setPositionMs(10000)
      .build();
  // Missing: assertion on the request body content
}
```