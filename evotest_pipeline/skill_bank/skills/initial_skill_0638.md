---
name: credit-card-number-prefix-validation
description: When validating credit card numbers by number prefixes and lengths, test
  that cards matching multiple patterns are classified correctly (not just the first
  match). Use when testing card issuer detection logic.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# credit-card-number-prefix-validation

## Instructions

# Credit Card Number Prefix Validation

## Instructions

- WHEN the TG encounters credit card number validation code that matches card numbers against multiple prefix patterns (e.g., VISA starts with "4", Switch starts with "4903", "4905", "4911", "4936")
- THEN the TG should write tests that use card numbers whose prefixes match MULTIPLE card types — for example, a number starting with "4905..." matches both VISA (starts with "4") and Switch (starts with "4905"). The test MUST verify that the correct (most specific) card type wins.
  - Specifically, test that a 16-digit number starting with "4905" is classified as **SWITCH**, NOT **VISA**.
  - Test that a 16-digit number starting with "4" but NOT matching any other prefix (e.g., "4000...") is classified as **VISA**.
  - Test that a 16-digit number starting with "4911" is classified as **SWITCH**, NOT **VISA**.
  - Test that a 16-digit number starting with "4936" is classified as **SWITCH**, NOT **VISA**.
  - Use the appropriate assertion method (e.g., `Assert.assertEquals(expected, actual)`) to compare the card type enum/constant.
- Common pitfalls:
  - Testing only non-ambiguous numbers (e.g., "4111..." which only matches VISA) and missing the ambiguous prefix cases
  - Assuming that the first matching prefix in declaration order determines the result
  - Using incorrect card number lengths that match neither type, causing false negatives
  - Testing only one ambiguous prefix when multiple exist

### Correct Example
```java
// Test that a Switch-prefixed number (4905...) is NOT misclassified as VISA
@Test
public void isVisa()
{
    // 16-digit number starting with "4905" — matches both VISA ("4") and Switch ("4905")
    // The correct classification should be SWITCH (more specific prefix wins)
    Assert.assertEquals(CreditCard.SWITCH, validator.check("4905 1234 5678 9012"));
}
```

### Incorrect Example
```java
// WRONG: Only testing non-ambiguous VISA numbers, missing the prefix overlap bug
@Test
public void isVisa()
{
    // This only tests "4111..." which ONLY matches VISA — doesn't catch the overlap
    Assert.assertEquals(CreditCard.VISA, validator.check("4111 1111 1111 1111"));
}
```