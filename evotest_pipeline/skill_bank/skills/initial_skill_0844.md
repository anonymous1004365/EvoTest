---
name: properties-placeholder-in-delay-pattern
description: WHEN a route uses delayPattern with a {{placeholder}} that resolves to
  a delay-pattern string, THEN the TG should test that the delay pattern from properties
  is properly parsed and applied during redelivery. This skill ensures delay patterns
  sourced via property placeholders work correctly with onException and dead letter
  channel error handlers.
code_tags:
- PROPERTY_PLACEHOLDER_RESOLUTION
- REDELIVERY_POLICY_CONFIG
test_pattern: PARAMETRIC_TEST
---

# properties-placeholder-in-delay-pattern

## Instructions

# Properties Placeholder in Delay Pattern

## Instructions

### WHEN conditions
Apply this skill WHEN the code under test involves any of these patterns:
- A route uses `.delayPattern("{{...}}")` on an `onException(...)` definition where the placeholder resolves to a delay pattern value (e.g., `"1:10000;2:20000"`)
- A route uses `.delayPattern("{{...}}")` on a `deadLetterChannel(...)` error handler builder
- A `RedeliveryPolicyDefinition` or `DefaultErrorHandlerBuilder` receives a `delayPattern` value that comes from a property placeholder resolution (using `{{...}}` syntax)

### THEN actions
The TG should:
1. **Create a properties file** on the test classpath that defines the placeholder (e.g., `myDelayPattern=1:10000;2:20000`)
2. **Configure the PropertiesComponent** in `createCamelContext()` to load the properties file (e.g., `pc.setLocations(new String[]{"classpath:...properties"})`)
3. **Build a route** that uses `onException(Exception.class).delayPattern("{{myDelayPattern}}").maximumRedeliveries(1).handled(true).to("mock:dead")` followed by `from("direct:start").throwException(new IllegalArgumentException("Forced"))`
4. **Verify that the exchange ends up in the dead letter channel** (`mock:dead`) after the configured redeliveries — this confirms the delay pattern was resolved and applied correctly
5. **Use `ContextTestSupport`** as the test base class, with `getMockEndpoint("mock:dead").expectedMessageCount(1)` and `template.sendBody("direct:start", ...)` followed by `assertMockEndpointsSatisfied()`

### What the test should catch
- The buggy version fails to properly resolve the property placeholder inside the delay pattern, causing the redelivery policy to malfunction — the exchange may not reach the dead letter channel or may behave incorrectly
- The fixed version correctly resolves the property placeholder, so the delay pattern is applied and redelivery works as expected

### Common pitfalls to avoid
- **Testing only literal delay patterns**: Do NOT test `.delayPattern("1:10000;2:20000")` as a literal string — that bypasses property resolution entirely. The bug is specifically about **property placeholder resolution inside delayPattern**.
- **Forgetting to include `handled(true)`**: Without `handled(true)`, the exception propagates and may cause the test to fail at `assertMockEndpointsSatisfied()` even on the fixed version.
- **Using wrong properties file path**: Make sure the properties file is accessible on the classpath and the path in `pc.setLocations(...)` matches exactly.
- **Not configuring PropertiesComponent**: The test must override `createCamelContext()` to add the `PropertiesComponent` with the properties file; otherwise placeholders won't be resolved.

### Example code

**Correct test (catches this bug):**

```java
public class PropertiesComponentOnExceptionDelayPatternTest extends ContextTestSupport {

    public void testDelayPattern() throws Exception {
        getMockEndpoint("mock:dead").expectedMessageCount(1);
        template.sendBody("direct:start", "Hello World");
        assertMockEndpointsSatisfied();
    }

    @Override
    protected RouteBuilder createRouteBuilder() throws Exception {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                onException(Exception.class)
                    .delayPattern("{{myDelayPattern}}")
                    .maximumRedeliveries(1)
                    .handled(true)
                    .to("mock:dead");

                from("direct:start")
                    .throwException(new IllegalArgumentException("Forced"));
            }
        };
    }

    @Override
    protected CamelContext createCamelContext() throws Exception {
        CamelContext context = super.createCamelContext();
        PropertiesComponent pc = new PropertiesComponent();
        pc.setCamelContext(context);
        pc.setLocations(new String[]{"classpath:org/apache/camel/component/properties/myproperties.properties"});
        context.addComponent("properties", pc);
        return context;
    }
}
```

With `myproperties.properties` containing:
```
myDelayPattern=1:10000;2:20000
```

**Incorrect test (does NOT catch this bug):**

```java
// ❌ Uses literal delay pattern instead of property placeholder
public class IncorrectTest extends ContextTestSupport {
    public void testLiteralDelayPattern() throws Exception {
        getMockEndpoint("mock:dead").expectedMessageCount(1);
        template.sendBody("direct:start", "Hello World");
        assertMockEndpointsSatisfied();
    }
    @Override
    protected RouteBuilder createRouteBuilder() throws Exception {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                onException(Exception.class)
                    .delayPattern("1:10000;2:20000")  // ❌ literal, no placeholder resolution
                    .maximumRedeliveries(1)
                    .handled(true)
                    .to("mock:dead");
                from("direct:start")
                    .throwException(new IllegalArgumentException("Forced"));
            }
        };
    }
}
```