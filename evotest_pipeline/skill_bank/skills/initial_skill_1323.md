---
name: template-proxy-type-validation
description: Teaches the TG how to test that setProxyFactory and similar Template
  methods accept all valid type arguments (e.g., String AND CtTypeReference), not
  just one specific type. This skill applies when a method parameter is of a general
  type (like Object) but only works with specific non-obvious subtypes.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
test_pattern: PARAMETRIC_TEST
---

# template-proxy-type-validation

## Instructions

# Template Proxy Type Validation

## Instructions

- WHEN the TG encounters a `setProxyFactory` method (or similar "setter" method on a template-like class) whose parameter type is `Object` or a very broad type — but the internal logic is documented/known to accept specific subtypes (e.g., `String` AND `CtTypeReference`), even though a cast/branching check exists in the fixed version
- THEN the TG should write a **parametric test** that passes BOTH a `String`-type proxy value AND a `CtTypeReference`-type proxy value to that setter, and verify that the getter returns the expected values without throwing an exception
- Include explicit null-argument tests to verify null-safety (should not throw NPE on set/get)
- The test should specifically verify that:
  - `setProxyFactory("someValue")` followed by `getProxyFactory()` returns the same value
  - `setProxyFactory(someCtTypeRef)` followed by `getProxyFactory()` returns the same value
  - `setProxyFactory(null)` does not throw an exception and/or the getter returns null
- **Common pitfall to avoid:** testing only `String`-type proxy values, because the original buggy code only handled `String` arguments and silently broke when a `CtTypeReference` argument was passed (e.g., by throwing a `ClassCastException`)

### Correct Example (pseudocode)

```java
@Test
public void testProxyFactoryWithDifferentTypes() {
    Template t = new TemplateImpl();
    
    // Test with String
    t.setProxyFactory("myProxyValue");
    assertEquals("myProxyValue", t.getProxyFactory());
    
    // Test with CtTypeReference
    CtTypeReference<?> ref = factory.Type().get(String.class);
    t.setProxyFactory(ref);
    assertEquals(ref, t.getProxyFactory());
    
    // Test with null
    t.setProxyFactory(null);
    assertNull(t.getProxyFactory());
}
```

### Incorrect Example (would NOT catch the bug)

```java
@Test
public void testProxyFactoryWithString() {
    Template t = new TemplateImpl();
    t.setProxyFactory("test");
    assertEquals("test", t.getProxyFactory());
    // Only tests String — would pass on both buggy and fixed versions
}
```