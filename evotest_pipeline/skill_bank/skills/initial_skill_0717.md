---
name: email-property-case-validation
description: This skill applies when a domain model object has properties with setter
  methods that should enforce case normalization (e.g., email addresses that must
  be stored in lowercase). The TG should test that setters normalize case for such
  properties, or that setters reject values that don't meet the case constraint.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- VALIDATION
test_pattern: STATE_TEST
---

# email-property-case-validation

## Instructions

# Email Property Case Validation

## Instructions

- WHEN the TG encounters a setter method for a string property that represents an email address (e.g., `setEmail(String email)` on a User domain model)
- THEN it should verify that the setter normalizes the property value to lowercase, or alternatively validates that the input is already lowercase
- Specifically, if the email setter is expected to call `.toLowerCase()` or equivalent before storing, the TG must write a test that:
  - Creates a new instance of the domain object (e.g., `new User()`)
  - Calls the setter with an email that contains uppercase characters (e.g., `"John.Doe@Example.Com"`)
  - Calls the corresponding getter (e.g., `getEmail()`)
  - Asserts that the returned value is all lowercase (e.g., `"john.doe@example.com"`)
- If the setter is NOT supposed to normalize case, the TG must test that an exception is thrown (e.g., `IllegalArgumentException`) when an uppercase email is passed, or that validation logic rejects it
- Common pitfalls:
  - Testing only with already-lowercase email addresses — this will pass even if the normalization is missing
  - Forgetting to call both setter and getter to observe the stored state
  - Assuming the property is stored directly without transformation — read the setter's implementation to confirm

### Correct Example (when setter normalizes to lowercase)

```java
// BAD: This test passes even if setEmail() doesn't normalize case
@Test
public void testEmailIsLowerCase_ineffective() {
    User user = new User();
    user.setEmail("john@example.com");
    assertEquals("john@example.com", user.getEmail());
    // This passes trivially — no uppercase was ever set
}

// GOOD: This test actually verifies case normalization
@Test
public void testEmailIsLowerCase() {
    User user = new User();
    user.setEmail("John.Doe@Example.Com");
    assertEquals("john.doe@example.com", user.getEmail());
    // Fails on buggy version if normalization is missing
}
```

### Correct Example (when setter should throw on uppercase)

```java
@Test(expected = IllegalArgumentException.class)
public void testEmailRejectsUppercase() {
    User user = new User();
    user.setEmail("John.Doe@Example.Com");
    // Should throw — no implicit normalization
}
```