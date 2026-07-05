---
name: number-suffix-boundary-accuracy
description: When formatting large numbers with suffix abbreviations (K/M/G/T), test
  boundary values where Math.log division can produce rounding errors that cause incorrect
  suffix selection or formatting.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ARITHMETIC_OVERFLOW
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# number-suffix-boundary-accuracy

## Instructions

# Number Suffix Boundary Accuracy

## Instructions

- WHEN the TG encounters code that uses `Math.log(value) / Math.log(base)` to compute an integer exponent for selecting a suffix (e.g., `{"", "K", "M", "G", "T", "P", "E", "Z"}`) and then divides by `Math.pow(base, exp)` to format a number with that suffix
- THEN the TG should test boundary values around each suffix transition, specifically:
  - For a base of **1000** or **1024**, test values like `base^exp - 1`, `base^exp`, and `base^exp + 1` for each exponent
  - For example, for base=1024, test `1024^1 - 1 = 1023` (should get suffix "" with commas), `1024^1 = 1024` (should get suffix "K"), `1024^2 - 1 = 1048575`, `1024^2 = 1048576` (should get suffix "M"), etc.
  - Also test the initial boundary: `base - 1` (should use df/df_mantissa without suffix) and `base` (should use first suffix)
  - Compare the expected format: e.g., `bigNumberForSize(1023)` should give something like `"1,023"` (comma-formatted, no suffix), while `bigNumberForSize(1024)` should give `"1.00K"`
- **Common Pitfall**: Only testing round/magic numbers (like 1024, 1048576) without also testing values just below the base, or testing only one type parameter (e.g., only `long` overloads, missing the `double` overloads). The bug manifests when `Math.log` floating-point imprecision causes the exponent to be miscalculated at exact power boundaries — e.g., `Math.log(1000) / Math.log(1000)` might yield `0.9999999` instead of `1.0`, causing the method to incorrectly choose the wrong suffix (e.g., using suffix `""` instead of `"K"`, or using `"K"` instead of `""`). This results in formatting like `"1.00K"` being returned where `"1,000"` is expected.

### Incorrect Example (does NOT catch the bug):
```java
// Only tests exact powers — misses the floating-point boundary issue
assertEquals("1.00K", NumUtil.bigNumberForQuantity(1000));
assertEquals("1.00K", NumUtil.bigNumberForSize(1024));
assertEquals("1.00M", NumUtil.bigNumberForSize(1048576));
```

### Correct Example (catches the bug):
```java
// Tests values just below the base threshold — this is where the bug manifests
assertEquals("999", NumUtil.bigNumberForQuantity(999));
assertEquals("1,000", NumUtil.bigNumberForQuantity(1000));  // BUG: returns "1.00K" instead!
assertEquals("1.00K", NumUtil.bigNumberForQuantity(1000));  // Expected on fixed version

// Additionally test with double overload
assertEquals("1,000.00", NumUtil.bigNumberForQuantity(1000.0)); // The double version has different path
```