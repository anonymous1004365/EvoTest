---
name: type-vs-mixin-ambiguity-resolution
description: When a method signature uses the same type for multiple parameters, and
  one parameter may hold values of a different concrete type at runtime via a generic
  wildcard or mixin, test each parameter's value validation independently with both
  expected and unexpected types to catch false-passing validations.
code_tags:
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# type-vs-mixin-ambiguity-resolution

## Instructions

# Type Ambiguity in Multi-Parameter Method Validations

## Instructions

**WHEN** the TG encounters a method that:
- Accepts two or more parameters of the same declared type (e.g., two `String` parameters, two `Object` parameters), AND
- One of those parameters is expected to hold values of a different runtime type (e.g., via a wildcard generic, a mixin, or an interface reference), AND
- The method validates or stores parameters in a way that relies on their values being of a specific subtype,

**THEN** the TG should write a parametrized test that:
1. Calls the method with a valid value for each parameter position to verify normal behavior.
2. Calls the method with an unexpected/incorrect type value in the **second** parameter (the one that should be validated against a different type expectation) while keeping the first parameter valid, and asserts that the method either throws an appropriate exception (e.g., `IllegalArgumentException`) or rejects the value (e.g., returns false/null).
3. Calls the method with an unexpected/incorrect type value in the **first** parameter while keeping the second parameter valid, to ensure both parameters are independently validated.
4. Tests with at least two distinct concrete types that are both **assignable** to the declared parameter type to trigger the ambiguity. For example, if parameters are declared as `String` but one is expected to be a path and another a property name, test with a path-like string in the property name position.

**Example (correct):** Given a method `void register(String key, String value)` where `key` is expected to be a valid identifier (alphanumeric) and `value` can be any string, the test should:
```java
@Test(expected = IllegalArgumentException.class)
public void testKeyValidationRejectsNonIdentifier() {
    // key parameter receives an invalid identifier — should throw
    instance.register("not-a-valid@key!", "some_value");
}

@Test
public void testValueAcceptsAnyString() {
    // value parameter receives arbitrary string — should succeed
    instance.register("valid_key", "not-a-valid@value!");
    // assert the value was stored as-is
}
```

**Example (incorrect):** Writing a test that only validates the first parameter and assumes the second is always valid:
```java
// BAD: Only tests key with valid identifier and a simple value
// Does NOT test key with invalid identifier
@Test
public void testRegistration() {
    instance.register("valid_key", "value");
    // passes even if validation is missing for the key
}
```

**Common Pitfalls:**
- Assuming that if two parameters have the same declared type, the validation logic treats them identically. In practice, one parameter may use a subtype, mixin, or wrapper internally.
- Only testing with two valid arguments of the same concrete type. Instead, vary the **semantic role** of each parameter: test with values that are appropriate for one role but inappropriate for the other.
- Forgetting to test both directional mismatches: valid-first/invalid-second AND invalid-first/valid-second, since validation may only guard one parameter.