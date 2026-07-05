---
name: jdk-version-range-boundary-testing
description: Teaches the TG to write thorough boundary tests for JDK version range
  expressions like [1.5,1.6], focusing on inclusive/exclusive bounds, edge cases with
  version string formats (e.g., "1.4.2_09-b03"), and the getRelationOrder method's
  token-splitting logic that may silently lose sub-tokens.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- TYPE_CONVERSION
- VERSION_RANGE_COMPARISON
- STRING_PARSING
test_pattern: PARAMETRIC_TEST
---

# jdk-version-range-boundary-testing

## Instructions

# JDK Version Range Boundary Testing

## Instructions

- WHEN the TG encounters a `JdkVersionProfileActivator` class with `isActive()`, `isInRange()`, or `getRelationOrder()` methods that parse JDK version strings (e.g., "1.4.2_09-b03") and compare them against range expressions (e.g., "[1.5,1.6]", "(1.3,1.6)", "[1.5,)", "(,1.6)")
- THEN the TG should write tests that:
  1. Test version strings containing underscores and hyphens (e.g., "1.4.2_09-b03") — the `getRelationOrder()` method strips non-numeric characters with `replaceAll("[^0-9\\.\\-\\_]", "")` but splits on `[\\.\\-\\_]`, which can cause the `Integer.parseInt()` to produce unexpected values when sub-tokens like `_09` or `-b03` are present
  2. Test exact boundary values for both lower and upper bounds:
     - For inclusive bounds `[lower,upper]`: test that `lower` returns true, `lower - epsilon` returns false, `upper` returns true, `upper + epsilon` returns false
     - For exclusive bounds `(lower,upper)`: test that `lower` returns false, `lower + epsilon` returns true, `upper` returns false, `upper - epsilon` returns true
  3. Test open-ended ranges: `[lower,)` (no upper bound) and `(,upper)` (no lower bound) — exercise the empty-string and "99999999" fallback in `getRange()`
  4. Test versions with differing precision (e.g., "1.5" vs "1.5.0" vs "1.5.0_09") — the `addZeroTokens()` method pads to 3 tokens, but the underscore splitting may alter comparisons
  5. Test the negation prefix `!` (e.g., "!1.4") to ensure it correctly inverts the prefix-match logic

- The test should use the `assertActivation(boolean expected, Profile profile, ProfileActivationContext context)` helper from `AbstractProfileActivatorTest` and construct profiles via `newProfile(String jdkVersion)` and contexts via `newContext(null, newProperties(String javaVersion))`

- Common mistakes to avoid:
  - Testing only clean version strings like "1.5.0" without underscore/hyphen variants like "1.5.0_09-b03" — the token-splitting logic treats `_` and `-` as delimiters, so "1.5.0_09" becomes tokens ["1","5","0","09"] but only the first 3 are used, making `_09` irrelevant to comparison
  - Testing only one format of range (e.g., only inclusive bounds) — all four range variants (`[a,b]`, `(a,b)`, `[a,)`, `(,b]`) should be tested
  - Assuming `isInRange()` works correctly for edge cases like empty version strings, null version strings, or malformed range expressions — the `getRelationOrder()` method returns hardcoded values for empty `rangeValue.value` (1 if isLeft, -1 otherwise)

### Correct Example (Test for inclusive bounds [1.5,1.6]):
```java
public void testVersionRangeInclusiveBounds() throws Exception {
    Profile profile = newProfile("[1.5,1.6]");
    
    // Below lower bound
    assertActivation(false, profile, newContext(null, newProperties("1.4")));
    assertActivation(false, profile, newContext(null, newProperties("1.4.2")));
    assertActivation(false, profile, newContext(null, newProperties("1.4.2_09")));
    assertActivation(false, profile, newContext(null, newProperties("1.4.2_09-b03")));
    
    // At lower bound
    assertActivation(true, profile, newContext(null, newProperties("1.5")));
    assertActivation(true, profile, newContext(null, newProperties("1.5.0")));
    assertActivation(true, profile, newContext(null, newProperties("1.5.0_09")));
    assertActivation(true, profile, newContext(null, newProperties("1.5.0_09-b03")));
    
    // Inside range
    assertActivation(true, profile, newContext(null, newProperties("1.5.1")));
    
    // At upper bound
    assertActivation(true, profile, newContext(null, newProperties("1.6")));
    assertActivation(true, profile, newContext(null, newProperties("1.6.0")));
    assertActivation(true, profile, newContext(null, newProperties("1.6.0_09")));
    assertActivation(true, profile, newContext(null, newProperties("1.6.0_09-b03")));
}
```

### Incorrect Example (Missing edge cases):
```java
// WRONG: Only tests clean version strings, no underscore/hyphen variants
public void testVersionRangeInclusiveBounds_incorrect() throws Exception {
    Profile profile = newProfile("[1.5,1.6]");
    
    assertActivation(false, profile, newContext(null, newProperties("1.4")));
    assertActivation(true, profile, newContext(null, newProperties("1.5")));
    assertActivation(true, profile, newContext(null, newProperties("1.6")));
    
    // Missing: versions with underscore like "1.5.0_09", "1.6.0_09-b03"
    // Missing: versions with differing precision like "1.5.0" vs "1.5"
}
```