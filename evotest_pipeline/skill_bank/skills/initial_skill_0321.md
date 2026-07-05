---
name: validator-resource-scope-resolution
description: When resource loaders resolve scopes for validator objects, test that
  both IValidator and IFormValidator types are handled, and that FormValidatorAdapter
  delegation works correctly to reach the underlying validator's class.
code_tags:
- VALIDATION
- CACHING_AND_CONVERTER_REGISTRY
test_pattern: STATE_TEST
---

# validator-resource-scope-resolution

## Instructions

# Validator Resource Scope Resolution

## Instructions

- **WHEN** the TG encounters code in a resource loader (e.g., `ValidatorStringResourceLoader`) that resolves the scope class from a validator object:
  - **THEN** it should test that both `IValidator` and `IFormValidator` types produce a valid, non-null scope class.
  - **THEN** it should specifically test that a `FormValidatorAdapter` wrapping an anonymous `IValidator` class correctly delegates to the underlying validator's class (not the adapter's class).
  - **THEN** the test should verify that `scope != null` and that `scope.getName()` returns the expected validator implementation's class name.

- **WHEN** the TG encounters a `FormValidatorAdapter` or `ValidatorAdapter` that wraps an `IValidator`:
  - **THEN** it should test that the adapter's `getValidator().getClass()` or equivalent method returns the *original* validator's class, not the adapter's own class.
  - **THEN** verify that the scope resolution does *not* return `ValidatorAdapter.class` or `FormValidatorAdapter.class` when called on an adapter wrapping an anonymous/inner class validator.

- **Common pitfalls to avoid:**
  - Testing only `IValidator` and forgetting to test `IFormValidator` adapter wrapping.
  - Using a named top-level `IValidator` class (like a lambda) that gives the same scope for both adapter and real validator — always test with an anonymous or inner class implementation.
  - Assuming `getClass()` called on the adapter returns the wrapped validator's class.

### Correct test pattern (testing scope resolution for FormValidatorAdapter):

```java
@Test
public void interfaceValidator()
{
    // Create an anonymous IValidator class
    IValidator<Object> validator = new IValidator<Object>()
    {
        @Override
        public void validate(IValidatable<Object> validatable)
        {
        }
    };

    IFormValidator formValidator = new FormValidatorAdapter(validator);
    Class<?> scope = validatorResourceLoader.getScope(formValidator);
    assertNotNull("Scope must not be null for FormValidatorAdapter", scope);
    // scope should be the anonymous validator's class, not FormValidatorAdapter
    assertEquals(validator.getClass().getName(), scope.getName());
}
```

### Incorrect test pattern (does not catch the bug):

```java
@Test
public void interfaceValidator()
{
    // Using a lambda — lambda class may behave differently than anonymous class
    IValidator<Object> validator = v -> {};
    IFormValidator formValidator = new FormValidatorAdapter(validator);
    Class<?> scope = validatorResourceLoader.getScope(formValidator);
    assertNotNull(scope);
    // Missing assertion on scope.getName() — does not verify correct class
}
```