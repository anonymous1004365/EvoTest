---
name: intercept-from-endpoint-uri-validation
description: Use this skill when testing interceptFrom with mixed endpoint reference
  types (URI strings and endpoint IDs). It teaches how to ensure interceptFrom correctly
  matches the intercepted endpoint URI, especially when endpoints are referenced by
  'ref:' or bean IDs instead of direct URI strings.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# intercept-from-endpoint-uri-validation

## Instructions

# InterceptFrom Endpoint URI Matching

## Instructions

- WHEN the TG encounters code that calls `RouteDefinition.interceptFrom(String)` or `InterceptFromDefinition` with an endpoint URI, AND the route contains endpoints defined by `ref:` prefix or bean IDs (not direct URI strings)
- THEN the TG should create a test that:
  1. Defines at least one endpoint in the registry by its URI (e.g., `"seda:bar"`) without a direct URI reference in the route
  2. Sets up an `interceptFrom()` with a specific URI string (e.g., `"seda:bar"`) that should match the registered endpoint
  3. Verifies that the interception actually triggers by asserting that messages passing through that endpoint get intercepted (e.g., `mock:intercepted` receives the exchange)
  4. Also tests that a different endpoint (not matched by the interceptFrom URI) does NOT get intercepted — `mock:otherEndpoint` should receive messages but `mock:intercepted` should not get those messages

- Common pitfalls:
  - Testing only `interceptFrom("*")` wildcard patterns instead of specific URI matching
  - Assuming that endpoints defined via `ref:` or bean IDs are matched by the same URI string as endpoints defined inline
  - Omitting verification that the interception actually fires (i.e., forgetting to confirm `mock:intercepted` was called)
  - Only testing with `from("direct:start")` style endpoints instead of `from("ref:endpointId")` style

### Correct Example:
```
// Register endpoint in the context (e.g., via camelContext.getRegistry().bind())
// Then define: interceptFrom("seda:bar")
// Route: from("ref:myBar").to("mock:end")
// Send a message: template.sendBody("seda:bar", "test")
// Verify: mock:intercepted received the message
```

### Incorrect Example (missing the ref-based endpoint case):
```
// Only testing: from("seda:bar").to("mock:end")
// This doesn't test the mixed ref+uri scenario that the bug is about
```