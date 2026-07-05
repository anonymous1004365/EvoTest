---
name: range-validator-exact-error-variable
description: When testing RangeValidator (or AbstractRangeValidator subclasses) in
  EXACT mode (min==max), verify that the ValidationError's "exact" variable is set
  to a non-null value matching the expected exact value. Without this, the test may
  silently pass on a buggy version.
code_tags:
- NULL_CHECK
- VALIDATION
- EXACT_VALUE_VARIABLE_IN_ERROR
test_pattern: STATE_TEST
---

# range-validator-exact-error-variable

## Instructions

# RangeValidator Exact Mode Error Variable Test

## Instructions

- WHEN the TG encounters a `RangeValidator` (or any `AbstractRangeValidator` subclass) constructed with `minimum == maximum` (i.e., EXACT mode), AND the test validates a value that falls OUTSIDE the valid range
- THEN the TG should write a test that: (1) validates an out-of-range value, (2) retrieves the resulting `ValidationError`, and (3) asserts that `error.getVariables().get("exact")` returns the correct non-null exact value (not null)

- **Common pitfall**: The TG might only check that `validatable.getErrors().size() == 1` (i.e., that an error was reported), without inspecting the error's `"exact"` variable. In the buggy version, the error was correctly added but the `"exact"` variable in the `ValidationError` was left as null (because `mode` was incorrectly computed as something other than `Mode.EXACT` when min==max). Only checking the error count would pass on both buggy and fixed versions, missing the bug.

- **Concrete types/values**: Use `RangeValidator<Integer>(1, 1)` (EXACT mode), validate with `Validatable<Integer>(2)`, then cast `validatable.getErrors().get(0)` to `ValidationError`, and assert `assertEquals(1, error.getVariables().get("exact"))`.

### Correct Example

```java
// Tests that the "exact" error variable is set when min==max
@Test
public void exact()
{
    IValidator<Integer> validator = new RangeValidator<Integer>(1, 1);

    Validatable<Integer> validatable = new Validatable<Integer>(2);
    validator.validate(validatable);
    assertEquals(1, validatable.getErrors().size());

    ValidationError error = (ValidationError) validatable.getErrors().get(0);
    assertEquals(1, error.getVariables().get("exact"));
}
```

### Incorrect Example (would NOT catch the bug)

```java
@Test
public void exact()
{
    IValidator<Integer> validator = new RangeValidator<Integer>(1, 1);

    Validatable<Integer> validatable = new Validatable<Integer>(2);
    validator.validate(validatable);
    assertEquals(1, validatable.getErrors().size());
    // BUG: does not check that error.getVariables().get("exact") is non-null
}
```

- **Why this matters**: Without the variable check, the test passes even when `getMode()` fails to return `Mode.EXACT` (e.g., when `max.equals(min)` is the condition but `max` is null, causing a NullPointerException that leaves the exact variable unset). The test passes on the buggy version because the error was still added — just missing the exact variable — giving a false sense of security.