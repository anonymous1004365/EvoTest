---
name: event-notifier-filtering-by-type
description: When an event notifier collects events of specific types (e.g., ExchangeSentEvent),
  the test should verify that only the expected event types are collected and that
  unrelated event types (e.g., ExchangeFailureHandledEvent) are NOT mistakenly delivered
  to the notifier's callback. Use this skill to catch bugs where the event notification
  framework fails to filter by event type correctly.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# event-notifier-filtering-by-type

## Instructions

# Event Notifier Filtering by Type

## Instructions

WHEN the TG encounters a test that registers a custom `EventNotifier` which filters events by type (e.g., using `getEventTypes()` to return a specific set of classes like `ExchangeSentEvent.class`), THEN the test should verify that only events matching the registered types are delivered to the notifier's callback, and that unrelated events (such as `ExchangeFailureHandledEvent`) are NOT delivered.

- WHEN the test configures a route that involves an error handler (e.g., `deadLetterChannel` or `defaultErrorHandler`) and the notifier is configured to only listen for `ExchangeSentEvent`, THEN the test should include an assertion that the notifier received zero events of the excluded type (e.g., `ExchangeFailureHandledEvent`). This catches cases where the event notification framework incorrectly dispatches all events regardless of the type filter.

- WHEN the `EventNotifier`'s `isEnabled(EventObject)` method checks the event type, THEN the test should verify that this method returns `true` for expected types and `false` for unexpected types. The test should assert the count or content of collected events, not just that the route completed successfully.

- WHEN using a `DefaultEventNotifier` subclass with custom `doNotify` logic, THEN the test should check the actual type of events passed to the notifier, not just the number of events. For example, assert that `event instanceof ExchangeSentEvent` is true for each collected event and `event instanceof ExchangeFailureHandledEvent` is false for all collected events.

Common pitfalls:
- Testing only that a route succeeds (e.g., arriving at a mock endpoint) without verifying which events were delivered to the notifier.
- Assuming that setting `getEventTypes()` is sufficient without asserting that excluded events are actually blocked.
- Not resetting/clearing event state between test cases, leading to false positives from prior test events.
- Using `Thread.sleep()` or waiting for a fixed time instead of properly synchronizing with event collection (use an `AtomicInteger` or similar counter synchronization).

### Correct Example (verifying event type filtering)

```java
public class EventNotifierFailureHandledEventsTest extends CamelTestSupport {
    // Use a list or counter to collect events
    private List<EventObject> events = new ArrayList<>();

    @Override
    protected CamelContext createCamelContext() throws Exception {
        CamelContext context = super.createCamelContext();
        EventNotifier notifier = new DefaultEventNotifier() {
            @Override
            protected void doNotify(EventObject event) throws Exception {
                events.add(event);
            }
            
            @Override
            public Set<Class<? extends EventObject>> getEventTypes() {
                // Only interested in sent events
                return new HashSet<>(Arrays.asList(ExchangeSentEvent.class));
            }
        };
        context.getManagementStrategy().addEventNotifier(notifier);
        return context;
    }

    @Test
    public void testOnlySentEventsAreDelivered() throws Exception {
        // route that fails and gets handled by dead letter channel
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                errorHandler(deadLetterChannel("mock:dead"));
                from("direct:start").to("mock:result");
            }
        });

        template.sendBody("direct:start", "Hello World");
        
        // Wait a bit for async events
        Thread.sleep(500);
        
        for (EventObject event : events) {
            assertTrue("Expected ExchangeSentEvent but got " + event.getClass().getName(),
                event instanceof ExchangeSentEvent);
            assertFalse("Should NOT receive ExchangeFailureHandledEvent",
                event instanceof ExchangeFailureHandledEvent);
        }
    }
}
```

### Incorrect Example (only checking route success)

```java
// BAD: Only checks that the exchange reached mock:dead
// Does not verify which events the notifier collected
@Test
public void testBadVerification() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            errorHandler(deadLetterChannel("mock:dead"));
            from("direct:start").to("mock:result");
        }
    });

    template.sendBody("direct:start", "Hello World");
    
    // This passes even if the notifier incorrectly received
    // ExchangeFailureHandledEvent events alongside ExchangeSentEvent events
    getMockEndpoint("mock:dead").expectedMessageCount(1);
    assertMockEndpointsSatisfied();
}
```