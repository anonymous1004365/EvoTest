---
name: notify-builder-from-route-null-endpoint
description: ''
code_tags:
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# notify-builder-from-route-null-endpoint

## Instructions

# NotifyBuilder fromRoute Predicate Null-Safety

## Instructions

- WHEN the TG encounters code that uses `NotifyBuilder.fromRoute(routeId)` to create a condition on `Exchange` instances
- THEN the TG should write a state verification test that:
  1. Creates a route that produces an exchange whose `Exchange.getFromEndpoint()` returns an endpoint whose URI does **not** contain a `«routeId»=` query parameter (e.g., a direct or seda endpoint without route ID metadata)
  2. Sends a message through that endpoint
  3. Asserts that `NotifyBuilder.matches(Exchange)` returns `false` (i.e., the exchange is **not** matched because it came from a different route)
  4. If the exchange comes from the correct route, asserts the builder returns `true`
- The test must verify that the predicate handles a null return from `EndpointHelper.getRouteIdFromEndpoint()` gracefully — i.e., it does NOT match all exchanges

- **Common pitfall**: Testing only exchanges whose `fromEndpoint` URI contains `routeId=...` — this masks the null-return case. The TG must test with endpoints that lack route ID metadata (e.g., `direct:start` without query parameters).

### Correct Example (pseudocode)
```java
// Arrange
NotifyBuilder builder = new NotifyBuilder(context).fromRoute("myRoute").whenDone(1);
// The exchange comes from an endpoint without routeId= in its URI
Exchange exchange = new DefaultExchange(context);
exchange.setFromEndpoint(context.getEndpoint("direct:start"));

// Act
boolean matches = builder.matches(exchange);

// Assert
assertFalse("Exchange from a different route should not match", matches);
```

### Incorrect Example (pseudocode)
```java
// BAD: Only testing exchanges whose fromEndpoint contains routeId=myRoute
// This never exercises the null-return branch in getRouteIdFromEndpoint()
Exchange exchange = new DefaultExchange(context);
exchange.setFromEndpoint(context.getEndpoint("direct:start?routeId=myRoute"));
assertTrue(builder.matches(exchange)); // Only tests the success path
```