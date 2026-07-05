---
name: throttler-jmx-consistency-under-async-delay
description: WHEN testing a Throttler configured with asyncDelayed=true via JMX, the
  test must ensure all exchanges complete despite asynchronous execution. This skill
  teaches how to await all messages via NotifyBuilder before asserting JMX counters.
code_tags:
- CONCURRENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# throttler-jmx-consistency-under-async-delay

## Instructions

# Throttler JMX Consistency Under Async Delay

## Instructions

- WHEN the TG encounters a `Throttler` processor configured with `asyncDelayed()` set to `true` (e.g., `.asyncDelayed()` in a route) AND the test checks JMX route counters (e.g., `MBeanServer.getAttribute(routeName, "ExchangesCompleted")`) AFTER sending messages to a `seda:` endpoint
- THEN the TG MUST:
  1. Use a `NotifyBuilder` to wait for at least half the messages to be received by the downstream endpoint before checking JMX counters. This is because async-delayed throttling means messages are queued on a separate thread pool and may not all have completed yet.
  2. Use `NotifyBuilder` with `.whenReceived(n)` where n is approximately half the total message count (e.g., for 10 total messages, wait for 5 received). Match the route's `from("seda:...")` endpoint from the "from" method.
  3. Call `notifier.matches(timeout, TimeUnit.SECONDS)` with a generous timeout like `2` seconds.
  4. Then call `assertMockEndpointsSatisfied()` to ensure all mock endpoints received the expected message count.
  5. ONLY THEN read the JMX attribute `ExchangesCompleted` from the route ObjectName and assert it equals the full message count (e.g., `10`).
- The typical assertion should be: `Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted"); assertEquals(10, completed.longValue());`
- This pattern prevents a race condition where the JMX counter has not yet been updated for the last few asynchronously-processed messages when the assertion is made.

### What to avoid (common pitfalls)
- Do NOT skip the `NotifyBuilder` await step when testing async-delayed Throttler via JMX — this will cause the `ExchangesCompleted` counter to be stale (e.g., returning 9 instead of 10).
- Do NOT use `NotifyBuilder.whenCompleted(n)` — use `whenReceived(n)` instead, since async-delayed exchanges may not be completed immediately.
- Do NOT use `Thread.sleep()` or other fixed-time waits — they are flaky and platform-dependent (the triggering test explicitly skips Windows and AIX platforms for this reason).
- NOTE: The `seda:` endpoint is used in the route, NOT `direct:` — this is because async-delayed throttling requires SEDA for non-blocking dispatch.
- Do NOT forget to reset the route counters with `mbeanServer.invoke(routeName, "reset", null, null)` before starting to send messages, if a previous batch was already sent.

### Correct Example
```java
public void testThrottleAsyncVisableViaJmx() throws Exception {
    // ... setup mock, JMX server etc.
    
    MBeanServer mbeanServer = getMBeanServer();
    ObjectName routeName = ObjectName.getInstance("org.apache.camel:context=camel-1,type=routes,name=\"route3\"");
    mbeanServer.invoke(routeName, "reset", null, null);

    getMockEndpoint("mock:endAsync").expectedMessageCount(10);

    NotifyBuilder notifier = new NotifyBuilder(context)
        .from("seda:throttleCountAsync").whenReceived(5).create();

    for (int i = 0; i < 10; i++) {
        template.sendBody("seda:throttleCountAsync", "Message " + i);
    }

    assertTrue(notifier.matches(2, TimeUnit.SECONDS));
    assertMockEndpointsSatisfied();

    Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
    assertEquals(10, completed.longValue());
}
```

### Incorrect Example (would fail on buggy version)
```java
// WRONG: No NotifyBuilder wait, races with async processing
public void testThrottleAsyncVisableViaJmx() throws Exception {
    MBeanServer mbeanServer = getMBeanServer();
    ObjectName routeName = ObjectName.getInstance("org.apache.camel:context=camel-1,type=routes,name=\"route3\"");
    mbeanServer.invoke(routeName, "reset", null, null);

    getMockEndpoint("mock:endAsync").expectedMessageCount(10);

    for (int i = 0; i < 10; i++) {
        template.sendBody("seda:throttleCountAsync", "Message " + i);
    }

    // Race condition: not all async messages may have completed yet
    assertMockEndpointsSatisfied();

    Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
    assertEquals(10, completed.longValue());  // May fail with expected:<10> but was:<9>
}
```