---
name: spring-bean-not-exists-null-validation
description: When a @SpringBean annotation is placed on a field but no matching bean
  exists in the Spring context, the proxy should return null instead of a proxy object
  with null target. This skill helps test that non-existent beans are properly handled.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- BEAN_PROPERTY_ASSIGNMENT
- ANNOTATION_PRESENCE_CHECK
test_pattern: STATE_TEST
---

# spring-bean-not-exists-null-validation

## Instructions

# Spring Bean Not-Exists Null Validation

## Instructions

- WHEN the TG encounters a field annotated with `@SpringBean` that references a bean name or type not registered in the Spring application context
- THEN it should create a test class with a field annotated with `@SpringBean(name="nonExistentBean")` (or use an interface/class type with no matching bean), instantiate the object using a dependency injection framework (e.g., `ProxyFieldValueFactory`), and verify that accessing the field returns `null` rather than a non-null proxy/lazy-initialization proxy object
- The test must create a Spring `ApplicationContext` that does NOT define the bean (or defines beans with different names), build the `AnnotProxyFieldValueFactory` (or equivalent) with that context, and call `getFieldValue()` on the annotated field to verify the result is `null`
- The test should catch the specific failure where the buggy code returns a `LazyInitProxyFactory$CGLibInterceptor` (or similar proxy) instead of `null`
- WHEN constructing the test, include the import `org.apache.wicket.spring.injection.annot.SpringBean` and ensure the test object's classpath is accessible to the Spring context
- Common pitfalls to avoid:
  - Testing only the case where the bean exists (happy path) and failing to test the non-existent bean case
  - Assuming that a non-existent @SpringBean simply returns `null` without needing to exercise the proxy factory
  - Using `@SpringBean` on a field with `name` attribute matching a non-existing bean, but not invoking `AnnotProxyFieldValueFactory.getFieldValue()`
  - Forgetting that the test must verify `null` specifically, not just that no exception is thrown

### Example (Correct):
```java
@Test
public void beanNotExists()
{
    ApplicationContext ctx = new ClassPathXmlApplicationContext("beans-no-such-bean.xml");
    AnnotProxyFieldValueFactory factory = new AnnotProxyFieldValueFactory(ctx);
    Field field = MyComponent.class.getDeclaredField("nonExistentBean");
    Object value = factory.getFieldValue(field, MyComponent.class);
    assertNull("Expected null for non-existent bean, but got: " + value, value);
}
```

### Example (Incorrect — missing the non-existent case):
```java
@Test
public void beanExists()
{
    ApplicationContext ctx = new ClassPathXmlApplicationContext("beans.xml");
    AnnotProxyFieldValueFactory factory = new AnnotProxyFieldValueFactory(ctx);
    Field field = MyComponent.class.getDeclaredField("myBean");
    Object value = factory.getFieldValue(field, MyComponent.class);
    assertNotNull(value);  // Only tests the happy path, misses the bug
}
```