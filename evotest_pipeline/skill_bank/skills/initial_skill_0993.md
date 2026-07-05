---
name: composed-constraint-notnull-required
description: When a custom constraint annotation (like @PasswordConstraintAnnotation)
  is itself annotated with @NotNull, PropertyValidator.isRequired() must return true.
  Use this skill when testing bean validation with composed constraints where @NotNull
  is declared on the annotation rather than directly on the property field.
code_tags:
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# composed-constraint-notnull-required

## Instructions

# Composed Constraint @NotNull Required Flag Resolution

## Instructions

### WHEN the TG encounters code that uses bean validation with composed constraints — specifically a custom constraint annotation that is itself annotated with `@NotNull` (e.g., `@PasswordConstraintAnnotation` has `@NotNull` on its own declaration), and this annotation is applied to a bean property:

- THEN the TG should test that `PropertyValidator.isRequired()` returns `true` for a `Property` whose field is annotated ONLY with the composed annotation (not directly with `@NotNull`).

- Create a test that:
  1. Defines a bean class with a property annotated with the composed constraint (e.g., `@PasswordConstraintAnnotation private String password;`).
  2. Constructs a `Property` object pointing to that bean class and property name: `new Property(BeanWithPassword.class, "password")`.
  3. Constructs a `PropertyValidator` using that `Property`: `new PropertyValidator<>(property)` — note: do NOT pass any groups.
  4. Asserts `assertTrue(propertyValidator.isRequired())`.

- The test must verify that the `ConstraintIterator` correctly traverses via `getComposingConstraints()` to find the `@NotNull` that lies on the composed annotation rather than directly on the property.

- **Common pitfalls to avoid:**
  - Testing only fields that have `@NotNull` directly declared on them, ignoring the composed constraint case.
  - Passing validation groups when the `@NotNull` on the composed annotation has no `groups` attribute (which means it applies to the `Default` group — the validator must have empty groups to match).
  - Assuming that `isRequired()` only checks direct annotations on the property; it must also traverse composed constraints.
  - Forgetting to use the full bean class (e.g., `BeanWithPassword.class`) rather than an anonymous or inner test class when referencing the property owner.

### Correct Example
```java
// Bean with a composed constraint that has @NotNull
public static class BeanWithPassword {
    @PasswordConstraintAnnotation  // This annotation is itself annotated with @NotNull
    private String password;
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}

// Test
@Test
public void testResolveComposedConstraints() {
    Property property = new Property(BeanWithPassword.class, "password");        
    PropertyValidator<BeanWithPassword> propertyValidator = new PropertyValidator<>(property);
    
    assertTrue(propertyValidator.isRequired());
}
```

### Incorrect Example (what to avoid)
```java
// ❌ BAD: Testing only direct @NotNull, not composed constraints
@Test
public void testDirectNotNull() {
    // Only tests a field with @NotNull directly declared
    Property property = new Property(TestBean.class, "property");
    PropertyValidator<TestBean> validator = new PropertyValidator<>(property);
    assertTrue(validator.isRequired());
    // This passes but misses the bug where composed @NotNull is NOT detected
}
```