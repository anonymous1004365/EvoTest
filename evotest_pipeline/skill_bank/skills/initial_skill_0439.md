---
name: builder-null-required-field-validation
description: When a Builder's build() method constructs an object with required fields,
  the test should verify that setting required fields to null (or not setting them)
  throws the correct exception. This catches missing validation in builder patterns.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- BUILDER_PATTERN
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# builder-null-required-field-validation

## Instructions

# Builder Null Required Field Validation

## Instructions

- WHEN the TG encounters a Builder class with a `build()` method that takes required fields or parameters (e.g., `DecryptionMaterialsRequest.builder().build()`)
- THEN it should write a test that calls `build()` **without** setting those required fields (or setting them to null/empty), and expect an exception such as `IllegalArgumentException`, `NullPointerException`, or `IllegalStateException`
- The test MUST construct the builder, call `setters` or `withXxx` methods for optional fields only (or none at all), then invoke `build()`, and verify the correct exception type and message is thrown
- Include tests for both **missing** (never set) and **explicitly null** values for each required field to ensure both paths are validated
- Common pitfalls: 
  - Testing only valid builder configurations and never testing missing/null required fields
  - Assuming that `null` default values in the builder will translate to null fields in the built object (the bug may be that null values silently pass through)
  - Testing builder setters in isolation without calling `build()` to trigger the validation logic
- Correct example (Java/JUnit 5):
  ```java
  @Test
  void build_withNullRequiredField_shouldThrow() {
      assertThrows(IllegalArgumentException.class, () -> {
          DecryptionMaterialsRequest.builder()
              .build();
      });
  }
  ```
- Incorrect example (missing the null-required-field edge case):
  ```java
  @Test
  void build_withAllFields_shouldSucceed() {
      DecryptionMaterialsRequest request = DecryptionMaterialsRequest.builder()
          .withAlgorithm(Algorithm.AES_256)
          .build();
      assertNotNull(request);
  }
  ```