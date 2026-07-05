---
name: bean-validation-composed-constraint-resolver
description: When testing Bean Validation property resolvers, ensure they correctly
  detect constraints from composed (@Valid-like) constraint annotations. The test
  should verify that the resolver's isRequired() method returns true when a property
  is annotated with a custom composed constraint that includes @NotNull, not just
  directly-applied annotations.
code_tags:
- VALIDATION
- COLLECTION_ITERATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# bean-validation-composed-constraint-resolver

## Instructions

# Bean Validation Composed Constraint Resolution

## Instructions

### WHEN the TG encounters code that resolves Bean Validation constraints from property annotations

- **THEN** the TG MUST test with composed (meta-annotated) constraint annotations — annotations that are themselves annotated with `@NotNull` (or other constraint annotations) — and verify that the resolver detects the composed constraint as a required/valid constraint.

- **WHEN** a `Validator` is used to iterate property constraints via `validator.getConstraintsForClass(owner).getConstraintsForProperty(propertyName).getConstraintDescriptors()`, and composing constraints are resolved via `getComposingConstraints()` on each `ConstraintDescriptor<?>`:

  - **THEN** the test MUST verify that the iteration over property constraints includes constraints defined through composed annotations (e.g., a custom annotation like `@PasswordConstraintAnnotation` that is itself annotated with `@NotNull`).
  - **THEN** the test MUST assert that `isRequired()` returns `true` for a property annotated with such a composed constraint.

- **WHEN** testing the `PropertyValidator` class or any similar constraint-resolving validator:

  - **THEN** create a test bean with a field annotated with a **custom composed constraint annotation** (e.g., `@PasswordConstraintAnnotation`) that itself carries `@NotNull`.
  - **THEN** instantiate a `Validator` (from a `ValidatorFactory`) and call `isRequired()` on the property.
  - **THEN** assert that the result is `true`.

- **Common pitfalls to avoid**:
  - ❌ Testing only directly-applied annotations like `@NotNull` or `@Size`, ignoring composed/meta-annotated constraints.
  - ❌ Assuming that `ConstraintDescriptor.getComposingConstraints()` is always empty or unimportant.
  - ❌ Using mocks for the `Validator` or `ConstraintDescriptor` that don't properly simulate composed constraint hierarchies.

### Correct Example

```java
// Create a test bean with a composed constraint
public class TestBean {
    @PasswordConstraintAnnotation  // this annotation is itself annotated with @NotNull
    private String password;
}

// The test
@Test
public void testComposedConstraintIsRequired() {
    ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
    Validator validator = factory.getValidator();
    
    Property property = new Property(TestBean.class, "password");
    PropertyValidator pv = new PropertyValidator();
    
    boolean required = pv.isRequired(property, validator);
    assertTrue("Property with @PasswordConstraintAnnotation (which has @NotNull) should be required", required);
}
```

### Incorrect Example (would miss the bug)

```java
@Test
public void testRequired() {
    // ❌ Only tests directly-applied @NotNull, misses composed constraint case
    ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
    Property property = new Property(SomeBean.class, "someField");  // field has @NotNull directly
    
    PropertyValidator pv = new PropertyValidator();
    assertTrue(pv.isRequired(property, factory.getValidator()));
}
```