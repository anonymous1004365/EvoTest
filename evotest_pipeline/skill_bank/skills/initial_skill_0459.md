---
name: null-exchange-handling-in-aggregation-bean-adapter
description: When an aggregation strategy bean adapter wraps a POJO, the method parameters
  for old/new exchange bodies may be evaluated via mandatoryBodyExpression, which
  throws an exception when the body is null. Test with null oldExchange to ensure
  the POJO method receives null rather than throwing a RuntimeException from the mandatory
  body evaluation.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# null-exchange-handling-in-aggregation-bean-adapter

## Instructions

# Null Exchange Handling in AggregationStrategyBeanAdapter

## Instructions

- WHEN the TG encounters code that invokes `AggregationStrategyBeanAdapter` with `allowNullOldExchange=true` or `allowNullNewExchange=true`, and a POJO method that accepts parameters via `ExpressionBuilder.mandatoryBodyExpression(Class<?>)` THEN the TG should test that both the oldExchange and newExchange can be `null` without throwing a `RuntimeException` (e.g. `InvalidPayloadException`).

- WHEN the TG sees `ExpressionBuilder.mandatoryBodyExpression(Class<?>)` being used to evaluate the body of an `Exchange` (as done in `AggregationStrategyBeanInfo.createMethodInfo()`), THEN the TG must verify that when the exchange is `null`, the code path does NOT call `mandatoryBodyExpression.evaluate()` on that null exchange. The bug occurs because `AggregationStrategyBeanInfo` always uses `mandatoryBodyExpression` to create parameter expressions, and `AggregationStrategyMethodInfo.invoke()` passes `null` for the exchange — but the expression was created with `mandatoryBodyExpression`, so when it tries to extract the body from a null exchange, it throws an exception instead of passing `null` to the POJO method.

- WHEN writing a test for a POJO aggregator like `MyAggregationBean` with a method such as `String aggregateUsers(String existingUsers, String newUsers)`, THEN the TG should test with `allowNullOldExchange(true)` and verify that when the first aggregation occurs (oldExchange is null), the POJO method receives `null` for the old exchange body parameter, i.e. the first parameter gets `null` instead of triggering a `InvalidPayloadException`.

- Common pitfalls to avoid:
  - Testing only with non-null exchanges — the bug only manifests when `oldExchange` or `newExchange` is `null` and the POJO parameter uses `mandatoryBodyExpression` for body extraction.
  - Assuming `allowNullOldExchange=true` is sufficient to prevent exceptions — it only controls whether `aggregate()` returns early; the method info still evaluates expressions on the null exchange.
  - Forgetting that the POJO method receives `null` values for parameters corresponding to a null exchange — the fix ensures that `AggregationStrategyMethodInfo.invoke()` passes `null` to the POJO method rather than throwing from the expression evaluation.

### Correct test approach:

```java
// POJO used in aggregation
public static class MyAggregator {
    public String addUsers(String existingUsers, String newUsers) {
        // existingUsers will be null on first call when allowNullOldExchange=true
        if (existingUsers == null) {
            return newUsers;
        }
        return existingUsers + "," + newUsers;
    }
}

@Test
public void testAggregationWithNullOldExchange() throws Exception {
    // Configure adapter with allowNullOldExchange=true
    MyAggregator aggregator = new MyAggregator();
    AggregationStrategyBeanAdapter adapter = new AggregationStrategyBeanAdapter(aggregator, "addUsers");
    adapter.setAllowNullOldExchange(true);
    
    // Create a context and start the adapter
    CamelContext context = new DefaultCamelContext();
    adapter.setCamelContext(context);
    adapter.start();
    
    // Create only a newExchange (simulating first aggregation)
    Exchange newExchange = new DefaultExchange(context);
    newExchange.getIn().setBody("user1");
    
    // This should NOT throw — oldExchange is null but method receives null
    Exchange result = adapter.aggregate(null, newExchange);
    assertNotNull(result);
    assertEquals("user1", result.getIn().getBody(String.class));
}
```

### Incorrect approach — what the buggy code does:

```java
// Buggy: When oldExchange is null, AggregationStrategyMethodInfo.invoke()
// calls ExpressionBuilder.mandatoryBodyExpression(oldType).evaluate(null, oldType)
// which throws InvalidPayloadException because it tries to extract body from null exchange
@Test
public void testAggregationWithNullOldExchange_buggy() throws Exception {
    // This test PASSES on the buggy version when it should FAIL
    // because the buggy code throws an exception when oldExchange is null
    
    MyAggregator aggregator = new MyAggregator();
    AggregationStrategyBeanAdapter adapter = new AggregationStrategyBeanAdapter(aggregator, "addUsers");
    adapter.setAllowNullOldExchange(true);
    
    CamelContext context = new DefaultCamelContext();
    adapter.setCamelContext(context);
    adapter.start();
    
    Exchange newExchange = new DefaultExchange(context);
    newExchange.getIn().setBody("user1");
    
    // Buggy version: throws InvalidPayloadException here
    Exchange result = adapter.aggregate(null, newExchange);
}
```