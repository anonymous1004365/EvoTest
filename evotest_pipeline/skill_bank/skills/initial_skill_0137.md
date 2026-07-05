---
name: credit-card-cardid-return-value
description: When testing card type identification via `determineCardId()`, assert
  the returned `CreditCard` enum value directly. The test should verify the correct
  enum constant (e.g., `CHINA_UNIONPAY`) is returned, not just that validation passes.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# credit-card-cardid-return-value

## Instructions

# Credit Card Type Detection — Assert Enum Return Values

## Instructions

- WHEN the TG encounters a method like `CreditCardValidator.determineCardId(String)` that returns a `CreditCard` enum (e.g., `CreditCard.CHINA_UNIONPAY`, `CreditCard.VISA`) to identify a credit card type
- THEN the TG should write a test that captures the return value and asserts it equals the expected `CreditCard` enum constant using `assertEquals(expected, actual)`
  - Example: `assertEquals(CreditCard.CHINA_UNIONPAY, validator.determineCardId("6222601010012578692"));`
- The test must use the specific `public final CreditCard determineCardId(String)` method, not just `validate()` which only returns pass/fail via `validatable.isValid()`
- The test should use realistic credit card numbers that pass the Luhn checksum check — the triggering test proved "6222601010012578692" is a valid China UnionPay number that passes all internal validation (length, prefix, Luhn checksum)
- WHEN testing a card type via `determineCardId()`, verify the correct `CreditCard` enum is returned — on the buggy version, a wrong implementation would return `CreditCard.INVALID` instead of the correct type, so the assertion `assertEquals(CreditCard.CHINA_UNIONPAY, creditCard)` would fail with `expected:<CHINA_UNIONPAY> but was:<INVALID>`

### Common Pitfalls
- Testing only via `validate()` + `validatable.isValid()` — this only tells you the number was accepted, not which card type was identified
- Using made-up credit card numbers that don't pass the Luhn checksum — the method returns `CreditCard.INVALID` for any number that fails `isChecksumCorrect()`, so test numbers must be realistic Luhn-valid numbers
- Forgetting to test each card type individually — the bug was specific to China UnionPay detection, so each card type needs its own `determineCardId()` test with a valid, representative number

### Example
**Correct** (catches the bug):
```java
@Test
public void isChinaUnionPay() {
    CreditCardValidator validator = new CreditCardValidator();
    CreditCard creditCard = validator.determineCardId("6222601010012578692");
    assertEquals(CreditCard.CHINA_UNIONPAY, creditCard);
}
```

**Incorrect** (misses the bug — only tests pass/fail, not card type):
```java
@Test
public void isChinaUnionPay() {
    CreditCardValidator validator = new CreditCardValidator();
    IValidatable<String> validatable = new Validatable<>("6222601010012578692");
    validator.validate(validatable);
    assertTrue(validatable.isValid());  // won't detect a wrong card type
}
```