---
name: quarter-format-invalid-inputs-return-null
description: When testing quarter/period formatting methods, the TG should verify
  that invalid or malformed inputs (null, empty, out-of-bounds values) cause the method
  to return null rather than crash, throw an exception, or produce incorrect formatted
  output. This skill covers validation of quarter formatting logic where input validation
  is the safety net.
code_tags:
- QUARTER_FORMAT_VALIDATION
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# quarter-format-invalid-inputs-return-null

## Instructions

# Quarter Format Validation: Invalid Inputs Should Return Null

## Instructions

- WHEN the TG encounters a method that formats a quarter string from numeric parameters (e.g., year and quarter number), or that accepts any kind of input intended for quarter/period formatting, THEN it should test invalid input combinations to ensure the method returns `null` (or equivalent sentinel) instead of producing garbage output or raising unexpected exceptions.

- WHEN testing quarter formatting with numeric inputs, the TG should include at least these invalid/edge-case parameter combinations:
  - Quarter number = 0 (should return `null`)
  - Quarter number = 5 (should return `null`)
  - Quarter number negative (should return `null`)
  - Year = negative number (should return `null`)
  - Year = 0 (should return `null`)

- WHEN the method uses a switch or if-else chain to map quarter numbers to formatted strings, the TG should ensure the test covers the boundary values just outside the valid range (e.g., 0 and 5 for a 1–4 range) to verify that the method has an explicit default/fallback that returns `null`.

- WHEN writing assertions, the TG should verify two things simultaneously:
  1. No exception is thrown (the method handles the invalid input gracefully)
  2. The return value is `null` (the method signals failure via null rather than returning a bogus formatted string)

- WHEN creating the test, the TG should avoid these common mistakes:
  - Testing only valid quarter values (1, 2, 3, 4) — this would never catch the validation bug
  - Asserting the method throws an exception for invalid input — the contract here is null-return, not throw
  - Testing only one invalid case — the bug might only manifest for certain invalid values (e.g., quarter=0 but not quarter=5, or vice versa), so test the full boundary set

### Example (Correct — Catches the Bug)

```java
@ParameterizedTest
@CsvSource({
    "2021, 0",   // quarter 0 is invalid → should return null
    "2021, 5",   // quarter 5 is invalid → should return null
    "2021, -1",  // negative quarter → should return null
    "-2021, 1",  // negative year → should return null
    "0, 1",      // year 0 → should return null
})
public void testFormatQuarter_InvalidInputs_ReturnsNull(int year, int quarter) {
    assertNull(H2msRestUtils.formatQuarter(year, quarter));
}
```

### Example (Incorrect — Would Miss the Bug)

```java
// ❌ Only tests valid quarters — never exercises the validation logic
@Test
public void testFormatQuarter_ValidInputs() {
    assertEquals("2021-Q1", H2msRestUtils.formatQuarter(2021, 1));
    assertEquals("2021-Q2", H2msRestUtils.formatQuarter(2021, 2));
    assertEquals("2021-Q3", H2msRestUtils.formatQuarter(2021, 3));
    assertEquals("2021-Q4", H2msRestUtils.formatQuarter(2021, 4));
}
```