---
name: component-depth-event-sink-type-traversal
description: When testing event broadcast with Broadcast.DEPTH, verify that the traversal
  order correctly visits component children in post-order AND non-component sinks
  (RequestCycle, Session, Application) are visited in the correct order. The test
  should use a concrete sink of each type and assert the visitation path.
code_tags:
- STATE_MUTATION
- COMPONENT_TREE_NAVIGATION
test_pattern: PARAMETRIC_TEST
---

# component-depth-event-sink-type-traversal

## Instructions

# Component Depth Event Sink Type Traversal

## Instructions

- WHEN the TG encounters a method that sends events using `Broadcast.DEPTH` with a non-Component `IEventSink` (e.g., `RequestCycle`, `Session`, or `Application`)
- THEN the TG should write a test that:
  1. Creates a `Component` tree (e.g., `Page`) with nested children
  2. Sends a payload to a non-Component sink (e.g., `page.send(requestCycle, Broadcast.DEPTH, payload)`)
  3. Records the order in which each sink's `onEvent()` is called
  4. Asserts that the visitation order is: all descendant components in post-order FIRST (deepest children first, then parents), THEN the non-Component sinks in bottom-up order: `RequestCycle` → `Session` → `Application`
- Common pitfall: Testing only `Broadcast.BREADTH` or only Component-to-Component `Broadcast.DEPTH`. Without this skill, the TG might write a Depth test using only a Component sink (e.g., `page.send(someComponent, Broadcast.DEPTH, payload)`) and miss the bug entirely because the bug only manifests when the sink is a non-Component type like `RequestCycle`.
- Common pitfall: Asserting the path incorrectly — for `Broadcast.DEPTH` with a non-Component sink, the component children must be visited in post-order (deepest-first) BEFORE the non-Component sinks. The non-Component sinks must be visited in the order: cycle → session → application (closest to the component first).
- The test should use a concrete payload class (e.g., a simple `Payload` object with no special behavior) and verify that each sink's `onEvent()` is invoked exactly once.

### Correct Example

```java
@Test
public void testDepth_Session() {
    // page is a WebPage, c12/c134/c135/c13/c1/c6 are its children
    // session is a mock Session, cycle is a mock RequestCycle, application is a mock Application
    // all implement IEventSink and record invocations in a List
    page.send(session, Broadcast.DEPTH, new Payload());
    // Children visited post-order: deepest leaf first, then their parents
    // Then non-Component sinks: cycle, session
    // Note: application is NOT visited because sink is Session (targetsSession=true, targetsApplication=false)
    assertPath(c12, c134, c135, c13, c1, c6, page, cycle, session);
}

@Test
public void testDepth_Application() {
    page.send(application, Broadcast.DEPTH, new Payload());
    // Children visited post-order: c12, c134, c135, c13, c1, c6, page
    // Then non-Component sinks: cycle, session, application
    assertPath(c12, c134, c135, c13, c1, c6, page, cycle, session, application);
}
```

### Incorrect Example

```java
// ❌ WRONG: Only tests Component-to-Component DEPTH, missing the bug
@Test
public void testDepth_Container() {
    page.send(c1, Broadcast.DEPTH, new Payload());
    assertPath(c12, c134, c135, c13, c1); // This works but doesn't exercise non-Component sinks
}

// ❌ WRONG: Wrong order assertion for non-Component sinks
@Test
public void testDepth_Application_wrongOrder() {
    page.send(application, Broadcast.DEPTH, new Payload());
    // Wrong: asserts application before cycle/session
    assertPath(c12, c134, c135, c13, c1, c6, page, application, cycle, session);
}
```