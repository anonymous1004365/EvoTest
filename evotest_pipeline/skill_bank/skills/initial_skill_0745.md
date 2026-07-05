---
name: empty-input-string-to-null-conversion
description: When validating text fields with type conversion (e.g., Integer, Long),
  test that empty string input is converted to null, not passed through type conversion.
  Without this check, empty strings can cause NumberFormatException during conversion.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# empty-input-string-to-null-conversion

## Instructions

# Empty Input String to Null Conversion in Type-Converted Text Fields

## Instructions

- WHEN the TG encounters a `convertInput()` method that extracts a raw string value from request parameters (e.g., `getRequest().getRequestParameters().getParameterValue(id)`) and then checks `convertEmptyInputStringToNull` to decide whether to set the converted input to `null`
- THEN the TG should write a test that:
  1. Creates a `TextField<Integer>` (or any type-converted TextField) with `setConvertEmptyInputStringToNull(true)` (the default)
  2. Simulates submitting the form with an **empty string** as the input value
  3. Calls `formComponent.processInput()` (or triggers validation) and verifies that `formComponent.getConvertedInput()` is `null`
  4. Verify that the validation **succeeds** (no error message is added) — empty input should be treated as null, not as a conversion error

- WHEN the `convertEmptyInputStringToNull` flag is involved
- THEN the test should include both cases:
  - **Case 1: `convertEmptyInputStringToNull = true` (default):** Empty string → converted input is `null`, no conversion error
  - **Case 2: `convertEmptyInputStringToNull = false`:** Empty string → converted input is still `null` or the unconverted empty string (depends on subclass behavior) — verify no `NumberFormatException` occurs

- Common pitfalls:
  - **Testing only with non-empty values** — this misses the bug entirely. Always add an empty-string test case.
  - **Assuming `TextField<Integer>` automatically handles empty strings** — without the null guard, the empty string `""` gets passed to integer conversion (`Integer.valueOf("")`), which throws `NumberFormatException`.
  - **Testing validation errors instead of conversion** — the bug is a `NumberFormatException` *before* validation. A clean test should verify the component does NOT throw an exception during `processInput()` and the converted input is `null`.
  - **Relying on existing tests without a specific empty-input case** — existing tests may use non-empty values and miss this edge case entirely.

### Example (correct test pattern):

```java
// Test: empty input is converted to null for Integer TextField
TextField<Integer> field = new TextField<Integer>("field", new Model<>(), Integer.class);
FormComponentTestHelper helper = new FormComponentTestHelper();
helper.getTester().getRequest().setParameter("field", "");
field.processInput();

// Verify no exception occurred and converted input is null
assertNull("Empty input should be converted to null", field.getConvertedInput());
assertFalse("No validation error should be added", field.hasErrorMessage());
```

### Example (incorrect — misses the bug):

```java
// BAD: Only tests with a valid integer value
TextField<Integer> field = new TextField<Integer>("field", new Model<>(), Integer.class);
helper.getTester().getRequest().setParameter("field", "42");
field.processInput();
assertEquals(Integer.valueOf(42), field.getConvertedInput());

// No empty-string test case — bug remains undetected!
```