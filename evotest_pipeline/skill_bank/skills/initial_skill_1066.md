---
name: policy-definition-and-transacted-definition-output-hierarchy
description: When testing DSL model definitions like PolicyDefinition and TransactedDefinition
  that extend OutputDefinition, the TG should verify that child processors/outputs
  are correctly managed and propagated, especially when the same route is traversed
  multiple times (e.g., via JMX route dump or route restart). Use this skill whenever
  you see a class extending an output-capable definition and the test involves restarting
  a route, dumping a route, or otherwise re-processing the processor hierarchy.
code_tags:
- USER_MANAGEMENT
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# policy-definition-and-transacted-definition-output-hierarchy

## Instructions

# PolicyDefinition/TransactedDefinition Output Management Bug

## Instructions

WHEN the TG encounters a `PolicyDefinition` or `TransactedDefinition` class (or any definition extending `OutputDefinition`) where:
- The definition's `createChildProcessor()` or similar method mutates internal state (e.g., setting `this.childProcessor` or modifying a list of outputs/processors)
- The test involves calling methods that traverse or re-traverse the route definition hierarchy (e.g., `getRoute().getOutputs()`, route dump, JMX operations like `dumpRouteAsXml`, route restart)
- The test uses a ManagedStrategy or JMX infrastructure to interact with the route multiple times

THEN the TG should:
1. **Verify processor list stability across multiple invocations**: Create a test that retrieves the route's processor definition hierarchy, triggers an operation that re-processes or dumps the route (e.g., `dumpRouteAsXml`), then re-retrieves and inspects the processor list. Assert that the list of child outputs/processors has NOT been mutated or truncated. For example, if the route initially has N processors, after the JMX dump or re-processing, it should still have N processors.

2. **Test with a custom Policy implementation**: Use a `Policy` implementation that is not a processor itself (i.e., `getProcessor()` returns `null` or a custom processor). Verify that definitions like `PolicyDefinition` and `TransactedDefinition` correctly handle the case where the policy's processor is null or custom, rather than assuming the policy IS the processor.

3. **Test idempotency of getOutputs()**: Call `getOutputs()` or equivalent on the definition object before and after an operation that processes the route. Assert that the returned list is the same size and contains the same elements in both invocations. The bug occurs when a definition's `createChildProcessor()` method overwrites internal state (e.g., setting `this.outputs` to a single-element list or nulling `this.childProcessor`), causing subsequent `getOutputs()` calls to return an incorrect (smaller) list.

4. **Expect specific failure on the buggy version**: On the buggy version, after performing a route dump operation (e.g., `managedRoute.dumpRouteAsXml(false)`), the number of outputs/processors reported should be smaller than expected. For example, a route with 3 processors should report only 1 processor after the dump operation. Assert that the number of processors (e.g., via `getRoute().getOutputs().size()`) is the expected value both before and after the destructive operation.

5. **Common pitfalls to avoid**:
   - Do NOT assume that `createChildProcessor()` is stateless or idempotent — it may mutate the definition's output list as a side effect.
   - Do NOT test only the initial state of the route; always test state AFTER a re-processing/dump operation.
   - Do NOT assume that `PolicyDefinition` and `TransactedDefinition` handle the case where `policy.getProcessor()` returns `null` — they may incorrectly treat the policy as the processor itself and overwrite `this.outputs`.
   - Do NOT test only with built-in processors; always include a custom `Policy` implementation that does NOT return itself as a processor.

## Example

### Correct Test (catches the bug)

```java
// Given a route with a custom policy and 3 processors
RouteDefinition route = context.getRouteDefinitions().get(0);
List<ProcessorDefinition<?>> outputs = route.getOutputs();
assertEquals("Before JMX dump, route should have 3 outputs", 3, outputs.size());

// When: the route is dumped via JMX (triggers re-processing of the definition hierarchy)
ManagedRouteMBean managedRoute = context.getManagedRoute(route.getId(), ManagedRouteMBean.class);
managedRoute.dumpRouteAsXml(false);

// Then: the number of outputs should remain unchanged
List<ProcessorDefinition<?>> outputsAfter = route.getOutputs();
assertEquals("After JMX dump, route should still have 3 outputs", 3, outputsAfter.size());
```

### Incorrect Test (misses the bug)

```java
// Only tests initial state — will pass even on buggy version
RouteDefinition route = context.getRouteDefinitions().get(0);
List<ProcessorDefinition<?>> outputs = route.getOutputs();
assertEquals("Route should have 3 outputs", 3, outputs.size());

// Does NOT re-process/re-dump the route, so the mutation bug is never triggered
```