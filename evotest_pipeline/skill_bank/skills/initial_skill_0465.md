---
name: listener-collection-mutation-during-iteration
description: Teaches how to test listener collections that throw ConcurrentModificationException
  or encounter order-dependent failures when listeners are added/removed during event
  dispatching. Apply when a listener collection iterates over a list while listeners
  may be added/removed by the callbacks.
code_tags:
- LISTENER_COLLECTION
- ORDER_DEPENDENCY
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# listener-collection-mutation-during-iteration

## Instructions

# Listener Collection Mutation During Iteration

## Instructions

- WHEN the TG encounters a listener collection class (e.g., `ListenerCollection<IRequestCycleListener>`) that implements a pattern similar to Java's `EventListenerList` — storing listeners in a list and iterating over them to dispatch events — THEN the TG should write a test that mutates the listener list **during** a dispatch cycle and verifies the behavior.

- WHEN the listener collection wraps its internal list with a `begin()`/`finish()` or similar mechanism (e.g., `add()` is deferred until after iteration completes), THEN the TG should verify that listeners added during iteration are NOT invoked for the current dispatch round, but ARE invoked for a subsequent round. Specifically:
  - Add one listener to the collection.
  - During that listener's callback, add a second listener to the same collection (e.g., `cycle.getListeners().add(newListener)`).
  - Assert that the second listener does NOT receive the event during the ongoing dispatch.
  - After the dispatch completes, trigger another dispatch and assert that the second listener DOES receive the event.

- WHEN the listener collection does NOT have a deferred-add mechanism (i.e., listeners are stored in a simple `ArrayList` and the `add()` method immediately appends), THEN the TG should expect a `ConcurrentModificationException` when listeners are added/removed during iteration. Write a test that:
  - Adds a listener that, when called back, adds another listener to the same collection.
  - Expects the operation to either succeed (depending on the collection's snapshot strategy) or throw `ConcurrentModificationException`.

- WHEN testing a `ListenerCollection` subclass that has multiple event types (e.g., `onBeginRequest`, `onEndRequest`, `onException`, etc.), THEN the TG should test each event type separately, because the bug may only manifest for certain events (e.g., `onBeginRequest` adds a listener that should receive `onEndRequest`).

- Common pitfalls to avoid:
  - ❌ Testing only with non-mutating listeners — this misses the mutation-during-iteration bug entirely.
  - ❌ Assuming that all listener collections use `CopyOnWriteArrayList` or other snapshot strategies — always check the actual implementation.
  - ❌ Not verifying both the pre-mutation and post-mutation state — the bug is about listeners added during iteration receiving events in the wrong order or not at all.
  - ❌ Using a single global mutable counter without resetting between test cases — this masks ordering bugs.

### Correct Example (testing deferred-add behavior)

```java
@Test
void listenerAddedDuringBeginRequest_ShouldNotReceiveBeginRequest_ButShouldReceiveEndRequest() {
    // Create a request cycle
    RequestCycle cycle = ...;
    
    // Use a list to track which events each listener received
    List<String> events = new ArrayList<>();
    
    // Listener A: adds Listener B during onBeginRequest
    IRequestCycleListener listenerA = new IRequestCycleListener() {
        @Override
        public void onBeginRequest(RequestCycle cycle) {
            events.add("A.begin");
            cycle.getListeners().add(new IRequestCycleListener() {
                @Override
                public void onBeginRequest(RequestCycle cycle) {
                    events.add("B.begin");
                }
                @Override
                public void onEndRequest(RequestCycle cycle) {
                    events.add("B.end");
                }
            });
        }
        @Override
        public void onEndRequest(RequestCycle cycle) {
            events.add("A.end");
        }
    };
    
    cycle.getListeners().add(listenerA);
    
    // First request cycle — B should NOT receive onBeginRequest
    cycle.scheduleRequestHandlerAfterCurrent(null);
    cycle.detach();
    
    // B.begin should NOT be in events
    assertThat(events).containsExactly("A.begin", "A.end");
    events.clear();
    
    // Second request cycle — B should now receive events
    cycle.scheduleRequestHandlerAfterCurrent(null);
    cycle.detach();
    
    assertThat(events).contains("A.begin", "B.begin", "A.end", "B.end");
}
```

### Incorrect Example (misses mutation-during-iteration)

```java
@Test
void testListenersWork() {
    RequestCycle cycle = ...;
    // Only tests a single, non-mutating listener — does NOT detect
    // the bug where listeners added during iteration are lost or cause CME
    cycle.getListeners().add(simpleListener);
    cycle.scheduleRequestHandlerAfterCurrent(null);
    cycle.detach();
    // No assertion about listener order or completeness during mutation
}
```