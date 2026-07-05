---
name: properties-component-route-config-validation
description: When a route uses property placeholders ({{key}}) alongside EIP methods
  like convertBodyTo(Class), the TG should test that the route correctly resolves
  placeholders even when configuration involves transacted policies or interceptors.
  This skill teaches how to build end-to-end Camel test cases that verify both property
  resolution and type conversion interact correctly.
code_tags:
- PROPERTY_PLACEHOLDER_RESOLUTION
- TYPE_CONVERSION
test_pattern: INTERACTION_TEST
---

# properties-component-route-config-validation

## Instructions

# Properties Component Route Configuration Validation

## Instructions

- WHEN the TG encounters a route that uses property placeholders (e.g., `{{myClassType}}`) in EIP methods such as `convertBodyTo`, `.to`, `.setHeader`, or `.bean`:
  - THEN the TG should create a test that:
    1. Sets the property in the `CamelContext`'s `PropertiesComponent` (e.g., `context.getPropertiesComponent().setLocation("ref:myProperties");` or via `@PropertySource` or `context.setProperty("myProp", "value")`) AND passes the property as a `RefPropertiesBean` or similar.
    2. Builds a route that uses the placeholder in at least one EIP method call, e.g. `convertBodyTo({{myType}})`.
    3. Sends a message through the route.
    4. Asserts the message body is of the expected converted type.

- WHEN the TG tests property placeholder resolution in combination with type conversion (e.g., `convertBodyTo`):
  - THEN the TG should ensure the test validates not only that the placeholder is resolved, but also that the body type is actually converted to the expected class. For example, if `{{myType}}` resolves to `java.lang.String`, then after `convertBodyTo({{myType}})`, the body must be of type `String`.
  - Include assertions like: `assertIsInstanceOf(byte[].class, result.getBody())` or `assertEquals(expectedString, result.getBody(String.class))`.

- WHEN the route configuration involves both property placeholders and transacted policies or interceptors:
  - THEN the TG should add a transacted policy (e.g., using `SpringTransactionPolicy`) or interceptors to the route, then verify the property placeholder still resolves correctly. This catches bugs where placeholder resolution is skipped or delayed due to early route processing.
  - Common pitfall: Testing property placeholder resolution only in simple routes without policies, missing the interaction bug between transacted/interceptor initialization and property resolution.

- WHEN constructing the test:
  - THEN the TG should use a `RefPropertiesBean` or directly set properties via `context.setProperty("key", "value")` before `context.start()`.
  - Expect that on the buggy version, the test may throw an exception (e.g., `IllegalArgumentException`, `TypeConversionException`, or produce a payload with incorrect type such as a `String` instead of `byte[]`).

- **Mistakes to avoid**:
  - Do NOT test property placeholders only by checking that the placeholder string is substituted; ALWAYS send a real message and verify the outcome.
  - Do NOT omit transacted policies or interceptors from the test — the bug manifests specifically when these are present.
  - Do NOT assume the type conversion happens after the placeholder resolves — the bug is that the type conversion is skipped because placeholder resolution fails early.
  - Do NOT use `@PropertySource` if the test needs to dynamically set properties — use `RefPropertiesBean` or direct `context.setProperty()`.

### Correct Example (Fixed version passes):
```java
RefPropertiesBean refProperties = new RefPropertiesBean();
refProperties.setProperty("myType", "byte[]");

context.setProperty("myProperties", refProperties);
context.getPropertiesComponent().setLocation("ref:myProperties");

context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("direct:start")
            .convertBodyTo({{myType}})
            .to("mock:result");
    }
});

template.sendBody("direct:start", "Hello World");
Exchange result = getMockEndpoint("mock:result").getReceivedExchanges().get(0);
assertIsInstanceOf(byte[].class, result.getBody());
```

### Incorrect Example (Misses the bug):
```java
// ❌ WRONG: Uses properties but no real message exchange to verify type conversion
context.getPropertiesComponent().setLocation("classpath:test.properties");
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("direct:start")
            .convertBodyTo({{myType}})
            .to("mock:result");
    }
});
// ❌ Missing: sending a message and checking the body type
// ❌ Missing: transacted policy or interceptor to trigger the bug path
```