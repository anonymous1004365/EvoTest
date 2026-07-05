---
name: template-param-type-breadth-testing
description: When a method accepts a generic Object parameter and internally checks
  its type (e.g., with instanceof), the TG should write tests passing objects of ALL
  supported types, not just the most common one. This ensures the type dispatch logic
  is correct for every branch.
code_tags:
- VALIDATION
- STRING_PARSING
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# template-param-type-breadth-testing

## Instructions

# Template Parameter Type Breadth Testing

## Instructions

- WHEN the TG sees a method that accepts a generic parameter type like `Object`, `String`, or a template variable `T`, and the method body contains type checks (e.g., `instanceof`, `getClass()`, or type-specific casting) that determine different behavior paths
- THEN the TG should write a parameterized test (or multiple explicit test methods) that passes objects of EACH distinct type handled by the conditional logic. Test with ALL concrete types the implementation checks for, not just the common/default type.
- Verify that for each input type, the correct behavior occurs (e.g., correct field is populated, correct exception is thrown, correct formatting is applied).
- **Common pitfalls to avoid**:
  - Testing only with the most obvious type (e.g., only `String` when the method also handles `CtTypeReference`)
  - Assuming the default/fallback branch covers all types
  - Writing a single test case that accidentally passes the same type for all parameters

### Correct Example (what the TG should write)

When testing a method that sets a field based on `Object` type checks:

```java
// Good: tests all handled types
@Test
public void testWithString() {
    TemplateParameter param = new TemplateParameter();
    param.setParameterType("foo.bar.Baz");
    assertEquals("foo.bar.Baz", param.getParameterTypeString());
    assertNull(param.getParameterTypeReference());
}

@Test
public void testWithCtTypeReference() {
    TemplateParameter param = new TemplateParameter();
    param.setParameterType(someCtTypeRef);
    assertEquals(someCtTypeRef, param.getParameterTypeReference());
    assertNull(param.getParameterTypeString());
}
```

### Incorrect Example (what the TG should avoid)

```java
// Bad: only tests String, misses CtTypeReference branch entirely
@Test
public void testParameterType() {
    TemplateParameter param = new TemplateParameter();
    param.setParameterType("foo.bar.Baz");
    assertEquals("foo.bar.Baz", param.getParameterTypeString());
}
```