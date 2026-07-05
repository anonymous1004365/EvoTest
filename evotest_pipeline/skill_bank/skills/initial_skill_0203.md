---
name: request-cycle-listener-onbegin-order
description: ''
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: STATE_TEST
---

# request-cycle-listener-onbegin-order

## Instructions

# Request Cycle Listener Firing Order

## Instructions

- WHEN the TG encounters a WebSocket processor (e.g., `AbstractWebSocketProcessor`, `TestWebSocketProcessor`, or any custom `IWebSocketProcessor`) that:
  - Uses `IRequestCycleListener` instances (via `RequestCycle` or `Session`)
  - Calls `onBeginRequest()` and `onEndRequest()` on those listeners
  - Also sends/modifies the WebSocket response (e.g., sends text/binary frames, closes the connection)

- THEN the TG MUST write a test that verifies the **order** of listener invocations:
  1. `onBeginRequest(requestCycle)` must be called **before** the response is committed (e.g., before `sendMessage()`, `sendBinary()`, or any write to the WebSocket connection).
  2. `onEndRequest(requestCycle)` must be called **after** the response is committed.

- The test should:
  - Create a custom `IRequestCycleListener` that records the order of calls (e.g., using a `List<String>` or a counter)
  - Register the listener via `Session.get().getRequestCycleListeners().add(listener)`
  - Invoke the WebSocket operation (e.g., open a connection, send a message, close)
  - Assert that `onBeginRequest` was called before any response was sent, and `onEndRequest` was called after
  - **Without this test**, the buggy version would fire `onEndRequest` but never fire `onBeginRequest` before the response, causing `NullPointerException` or missing state in listeners

- Common pitfalls:
  - ❌ Testing only that `onEndRequest` is called, without also verifying `onBeginRequest` order relative to response commit
  - ❌ Registering the listener on `Application` (global) instead of `Session` (per-request)
  - ❌ Not using a custom listener that verifies call order (e.g., using a `RecordingListener` class)
  - ❌ Only testing with a single listener — test with multiple listeners to ensure ALL get both events

## Example (correct)

```java
@Test
public void onBeginRequestFiredBeforeResponseCommit() {
    // Create a listener that records events
    IRequestCycleListener recorder = new AbstractRequestCycleListener() {
        private final List<String> events = new ArrayList<>();
        
        @Override
        public void onBeginRequest(RequestCycle cycle) {
            events.add("onBeginRequest");
        }
        
        @Override
        public void onEndRequest(RequestCycle cycle) {
            events.add("onEndRequest");
        }
        
        public List<String> getEvents() {
            return events;
        }
    };
    
    // Register on session
    Session.get().getRequestCycleListeners().add(recorder);
    
    // Perform WebSocket operation (e.g., open connection)
    WebSocketTester tester = new WebSocketTester();
    tester.open();
    
    // Assert order: onBeginRequest before onEndRequest
    List<String> events = recorder.getEvents();
    assertEquals("onBeginRequest", events.get(0));
    assertTrue(events.indexOf("onBeginRequest") < events.indexOf("onEndRequest"));
}
```

## Example (incorrect)

```java
// ❌ Only validates that onEndRequest was called, missing the order relative to response commit
@Test
public void testOnEndRequestFired() {
    // ... registers listener ...
    tester.open();
    // Only checks end
    assertTrue(recorder.onEndRequestCalled);
    // Does NOT check that onBeginRequest was called first
}
```