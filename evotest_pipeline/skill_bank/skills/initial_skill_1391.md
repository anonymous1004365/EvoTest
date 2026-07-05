---
name: outheaders-parameter-type-validation
description: When a bean method parameter is annotated with @OutHeaders, the parameter
  must be of type Map or a supertype of Map. This skill teaches the TG to detect and
  test type mismatches on @OutHeaders-annotated parameters.
code_tags:
- NULL_CHECK
- VALIDATION
- OUTHEADERS_PARAMETER_MAPPING
test_pattern: EXCEPTION_TEST
---

# outheaders-parameter-type-validation

## Instructions

# @OutHeaders Parameter Type Validation

## Instructions

- WHEN the TG encounters a bean method that has a parameter annotated with `@OutHeaders` (from `org.apache.camel.OutHeaders`)
  - THEN it should verify that the parameter type is `java.util.Map` or a supertype/interface of `Map`
  - THEN it should write a test that defines a bean class with a method where an `@OutHeaders`-annotated parameter has a non-Map type (e.g., `String`, `Integer`, `List<String>`, a custom class)
  - THEN the test should send a message to the bean via Camel's producer template and assert that the exchange fails with an `IllegalArgumentException` whose message contains "should be of type Map, not"
  - THEN the test should use the `@OutHeaders` annotation on a method parameter whose type is NOT `Map` or assignable to `Map`

- Common pitfalls to avoid:
  - Testing only with `Map`-typed parameters (those pass correctly; the bug only manifests with non-Map types)
  - Omitting the `@OutHeaders` annotation on the non-Map parameter (the validation only triggers when the annotation is present)
  - Expecting a different exception type (the bug triggers `IllegalArgumentException`, not `InvocationTargetException` or `RuntimeException`)
  - Testing with `@Headers` instead of `@OutHeaders` (the bug is specific to `@OutHeaders` validation logic)

### Example (correct test structure)

```java
public class BeanWithOutHeadersTypeMismatchTest extends ContextTestSupport {
    
    public static class MyBean {
        public void process(@OutHeaders String outHeaders) {
            // Bug: String is not a Map
        }
    }

    public void testOutHeadersWithInvalidType() throws Exception {
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                from("direct:start").bean(MyBean.class);
            }
        });
        
        try {
            template.sendBody("direct:start", "test");
            fail("Should have thrown an IllegalArgumentException");
        } catch (CamelExecutionException e) {
            assertTrue(e.getCause() instanceof IllegalArgumentException);
            assertTrue(e.getCause().getMessage().contains("should be of type Map, not"));
        }
    }
}
```

### Example (incorrect — would miss the bug)

```java
// ❌ BAD: Tests only with Map type — passes even without the fix
public void testOutHeadersWithMapType() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").bean(MyBeanWithMapParam.class);
        }
    });
    template.sendBody("direct:start", "test");
    // No exception thrown — this doesn't test the bug
}

// ❌ BAD: Tests with @Headers instead of @OutHeaders — different annotation, different code path
public void testHeadersAnnotation() throws Exception {
    // ...
}

// ❌ BAD: Omits the annotation entirely — no validation triggered
public void testNoAnnotation() throws Exception {
    // ...
}
```