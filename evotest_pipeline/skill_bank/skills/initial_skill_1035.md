---
name: splitter-method-call-routes-deferred-resolution
description: When testing Camel Splitter EIP with method call expressions across VM
  endpoints, ensure routes referencing beans are defined with proper deferred resolution.
  Tests may pass as standalone but fail in different contexts because method-call-to-bean
  splits rely on route definition ordering and context startup timing.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: INTERACTION_TEST
---

# splitter-method-call-routes-deferred-resolution

## Instructions

# Splitter Method Call Routes Deferred Resolution

## Instructions

- WHEN the TG encounters a Camel route that uses `.split().method("someMethod")` on a bean that is not explicitly defined in the same RouteBuilder's `configure()` method (e.g., the bean comes from a parent class, registry lookup, or is set via setter injection)
- THEN the TG must ensure that the test:
  1. Defines the bean in the `configure()` method of the RouteBuilder where the split is used, OR ensures the bean is available in the registry before context startup
  2. Uses `@Before` or route definition ordering that guarantees the splitter's bean is registered BEFORE the split route processes any messages
  3. Tests with an endpoint that goes through a Camel component (e.g., VM, SEDA, Direct) to exercise the full context lifecycle — not just unit-testing the splitter in isolation
- Common pitfalls to avoid:
  - Defining the splitter bean in a parent RouteBuilder's `configure()` and the split route in a child, relying on RouteBuilder ordering that may not be guaranteed
  - Testing the split method call only with `ProducerTemplate` direct sends without going through a VM/SEDA endpoint that could expose context lifecycle issues
  - Assuming that if a route starts successfully, bean references in `.method()` calls are fully resolved at route execution time — the method reference may fail silently if the bean was not available at context startup
- Verify that `mock:result` endpoints receive the expected split count (e.g., 3 messages split from a collection of 3 items). When the bean/method resolution fails, the split may produce 0 messages or the original unsplit message body.