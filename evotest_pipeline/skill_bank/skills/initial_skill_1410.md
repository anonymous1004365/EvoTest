---
name: china-unionpay-credit-card-validation
description: When testing CreditCardValidator's credit card number detection for China
  UnionPay cards, the test must use a Luhn-valid number that starts with 622 and falls
  within the 622126-622925 range and has length 16-19. This skill helps write tests
  that verify the isChinaUnionPay method correctly identifies valid China UnionPay
  numbers.
code_tags:
- NULL_CHECK
- VALIDATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# china-unionpay-credit-card-validation

## Instructions

# China UnionPay Credit Card Validation

## Instructions

- WHEN the TG encounters a test method `isChinaUnionPay()` in `CreditCardValidatorTest.java` that calls `determineCardId("6222601010012578692")` to verify `CreditCard.CHINA_UNIONPAY` is returned
- THEN the TG should verify that the test uses a valid China UnionPay credit card number that:
  1. Starts with "622" and falls within the range 622126-622925 (prefix check)
  2. Has a total length between 16 and 19 digits
  3. Passes the Luhn checksum algorithm
  4. The number `"6222601010012578692"` has length 19 and passes all checks
- The test should call `validator.determineCardId(number)` and assert the result equals `CreditCard.CHINA_UNIONPAY` using `assertEquals(CreditCard.CHINA_UNIONPAY, creditCard)`
- Common pitfalls the TG should avoid:
  - Using a China UnionPay number that does NOT pass the Luhn checksum — such numbers will be rejected early in `determineCardId()` before any card type matching occurs
  - Using a number starting with 622 but outside the 622126-622925 range (the `isChinaUnionPay()` private method checks the numeric prefix range, not just the "622" string prefix)
  - Forgetting that `determineCardId()` first validates length (12-19) and Luhn checksum before attempting card type identification — numbers failing those checks return `CreditCard.INVALID`
  - Not importing `CreditCardValidator.CreditCard` (used as `CreditCardValidator.CreditCard` or via static import)
  - Testing through `validate()` instead of `determineCardId()` — the bug is specifically in card type identification, which requires directly testing `determineCardId()` to observe the returned enum value

**Correct example:**
```java
@Test
public void isChinaUnionPay()
{
    CreditCardValidator validator = new CreditCardValidator();
    CreditCard creditCard = validator.determineCardId("6222601010012578692");
    assertEquals(CreditCard.CHINA_UNIONPAY, creditCard);
}
```

**Incorrect examples:**
```java
// WRONG: 622 prefix but NOT in 622126-622925 range (622000... is outside range)
CreditCard creditCard = validator.determineCardId("6220001111111111");
assertEquals(CreditCard.CHINA_UNIONPAY, creditCard); // Will fail - returns INVALID

// WRONG: Not Luhn-valid — even with correct prefix, will fail checksum check
CreditCard creditCard = validator.determineCardId("6221261234567890");
assertEquals(CreditCard.CHINA_UNIONPAY, creditCard); // Will fail - returns INVALID

// WRONG: Using validate() instead of determineCardId() — validate() only returns valid/invalid
IValidatable<String> validatable = new Validatable<>("6222601010012578692");
validator.validate(validatable);
// Cannot assert the CreditCard type was CHINA_UNIONPAY
```