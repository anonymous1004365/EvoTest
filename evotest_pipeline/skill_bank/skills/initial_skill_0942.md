---
name: bean-wrapper-primitive-property-assignment
description: When using reflection to set bean properties, primitive-typed setters
  may fail with boxed values that cannot be unboxed. Tests must verify that BeanWrapper/Reflection-based
  property assignment works correctly for both primitive and reference-type properties.
code_tags:
- BEAN_PROPERTY_ASSIGNMENT
- REFLECTION_PRIMITIVE_HANDLING
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# bean-wrapper-primitive-property-assignment

## Instructions

# Bean Wrapper Primitive Property Assignment via Reflection

## Instructions

- WHEN the TG encounters a `BeanWrapper` (or similar reflection-based property accessor) that uses `Method.invoke()` to call setter methods on a target object
- THEN it should write a parametric test that exercises property assignment for each property of the target class, covering BOTH primitive types (e.g., `int`, `long`, `boolean`) AND reference types (e.g., `String`, `Object`). The test should verify that after calling `setProperty(propertyName, value)` on the wrapper, the underlying bean's getter returns the correct value.
- Include test cases where the setter parameter is a primitive type but the value passed is its boxed equivalent (e.g., `Integer.valueOf(42)` for an `int` setter) — the reflection layer must handle unboxing correctly.
- Expect that if the reflection code fails to handle primitive-to-boxed conversions (e.g., by directly passing the boxed value without proper type conversion), an `IllegalArgumentException` will be thrown when `Method.invoke()` is called.
- **Common pitfall**: Testing only with `String` or `Object` properties and assuming reflection works uniformly for all types. Always include properties with primitive setters (e.g., `setX(int)` ) to catch reflection type-mismatch bugs.
- **Common pitfall**: Forgetting that the test must read back the property value via the wrapper's getter to verify the property was actually set on the bean, not just that no exception was thrown.

### Correct Example

```java
// Given a bean class with mixed primitive and reference properties
class SampleBean {
    private String name;
    private int age;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}

// Test with BOTH types
@Test
void shouldSetPrimitiveAndReferenceProperties() {
    SampleBean bean = new SampleBean();
    BeanWrapper wrapper = new BeanWrapperImpl(bean);
    
    wrapper.setPropertyValue("name", "John");  // reference setter
    wrapper.setPropertyValue("age", 30);        // primitive setter (autoboxed to Integer)
    
    assertEquals("John", wrapper.getPropertyValue("name"));
    assertEquals(30, wrapper.getPropertyValue("age"));  // fails if primitive unboxing is broken
}
```

### Incorrect Example (Misses the Bug)

```java
@Test
void shouldSetStringProperty() {
    SampleBean bean = new SampleBean();
    BeanWrapper wrapper = new BeanWrapperImpl(bean);
    wrapper.setPropertyValue("name", "John");
    assertEquals("John", wrapper.getPropertyValue("name"));
}
// This test passes even when primitive setter reflection is broken!
```