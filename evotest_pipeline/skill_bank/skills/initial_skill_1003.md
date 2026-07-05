---
name: condition-router-parameter-type-validation
description: WHEN writing tests for condition-based routers that accept collections
  of parameters with mixed types, THEN test with multiple parameter types (String,
  CtTypeReference, etc.) to ensure the router correctly matches against all valid
  types. This skill specifically applies to Dubbo's ConditionRouter matchFilter logic
  where proxy template parameters may be of different types.
code_tags:
- VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# condition-router-parameter-type-validation

## Instructions

# Condition Router Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a ConditionRouter implementation that filters invocations based on template parameters (e.g., `proxyTemplateParameters` in the parameters map)
- THEN it should write a parametric test that exercises the router with parameters of different concrete types, specifically:
  - `String` type parameters
  - `com.alibaba.dubbo.common.bytecode.Wrapper.CtTypeReference` or other non-String reference types
  - Verify that the route condition correctly matches against all supported types, not just String
- Include a test where the `invoke` method receives an invocation whose `proxyTemplateParameters` (stored under `"proxyTemplateParameters"` key in the parameters map) contains values of different types, and verify that `ConditionRouter.route()` returns the correct set of invokers
- The test should verify that no `ClassCastException` or incorrect routing occurs when non-String parameter values are present
- Common pitfalls to avoid:
  - Testing only with `String` type parameters, which masks the bug where type casting fails for non-String references
  - Assuming all template parameters are always `String` instances
  - Not covering the `matchFilter` path where `entry.getValue()` is compared against parameter values of different types
  - Forgetting to construct `invoke` invocations with properly populated `$invoker` and proxy template parameters

## Example Test Pattern (Correct)

```java
@Test
public void testRoute_matchFilter_MixedParameterTypes() {
    // Setup router with a condition that matches on proxy template parameter
    URL url = URL.valueOf("condition://0.0.0.0/com.foo.BarService")
        .addParameter("method", "sayHello,*
        .addParameter("parameters", "proxyTemplateParameters = targetParam");
    
    ConditionRouter router = new ConditionRouter(url);
    
    // Create an invocation with mixed parameter types
    Map<String, Object> params = new HashMap<>();
    params.put("proxyTemplateParameters", Arrays.asList("stringValue", someCtTypeReferenceObject));
    
    Invocation invocation = new RpcInvocation("sayHello", new Class<?>[0], new Object[0], params);
    
    List<Invoker<Object>> invokers = new ArrayList<>();
    // ... add invokers that should match based on the condition
    
    List<Invoker<Object>> result = router.route(invokers, url, invocation);
    assertNotNull(result);
    assertTrue(result.contains(expectedInvoker));
}
```

## Example Test Pattern (Incorrect — misses the bug)

```java
@Test
public void testRoute_matchFilter_OnlyStringParams() {
    // BAD: Only tests with String parameters, won't catch ClassCastException
    Map<String, Object> params = new HashMap<>();
    params.put("proxyTemplateParameters", Arrays.asList("value1", "value2"));
    // ... rest of test
    // This passes even on the buggy version, giving false confidence
}
```