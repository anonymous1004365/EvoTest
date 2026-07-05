---
name: message-history-defensive-copy
description: When Exchange properties contain mutable collection-typed values like
  MessageHistory lists, copies must use defensive copying (e.g., new LinkedList<>(original))
  to prevent shared references between the original and copied exchange. Apply when
  testing copy() or safeCopy() behavior on exchanges with list/collection properties.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# message-history-defensive-copy

## Instructions

# Message History Defensive Copy

## Instructions

- WHEN the code has a `copy()` or `safeCopy()` method on an Exchange implementation (e.g., `DefaultExchange.copy(boolean safeCopy)`) that copies exchange properties via `safeCopyProperties(getProperties())`
- THEN the test MUST verify that mutable collection-typed exchange properties (especially `Exchange.MESSAGE_HISTORY` / `"CamelMessageHistory"`) are NOT shared between the original exchange and its copy after the copy operation
- Specifically: after copying an exchange that has message history enabled (via `context.setMessageHistory(true)`), retrieve the property `Exchange.MESSAGE_HISTORY` (a `List<MessageHistory>`) from both the original and the copy, and assert that they are **different object references** using `assertNotSame()`
- The test should configure at least two mock endpoints (e.g., `mock:a` and `mock:b`) on a route so that each received exchange carries its own `MESSAGE_HISTORY` property, then verify that the list instances obtained from each endpoint are not the same object
- Common mistake to avoid: testing only the `assertNotEquals()` (value comparison) instead of `assertNotSame()` (reference comparison) — the bug is that the list reference is shared, not that its contents differ
- Another mistake: testing the copy without ensuring message history is enabled (`context.setMessageHistory(true)`) — without this, the `MESSAGE_HISTORY` property will not be populated on the exchanges

### Correct pattern:
```java
MockEndpoint a = getMockEndpoint("mock:a");
a.expectedMessageCount(1);
MockEndpoint b = getMockEndpoint("mock:b");
b.expectedMessageCount(1);

template.sendBody("seda:start", "Hello World");
assertMockEndpointsSatisfied();

List listA = (List) a.getReceivedExchanges().get(0).getProperty(Exchange.MESSAGE_HISTORY);
List listB = (List) b.getReceivedExchanges().get(0).getProperty(Exchange.MESSAGE_HISTORY);

// The fix ensures each exchange gets its own defensive copy of the list
assertNotSame("MESSAGE_HISTORY lists must not be the same object reference", listA, listB);
```

### Wrong pattern (would pass on buggy code):
```java
// Only checking values equality, not reference identity
assertEquals(listA.size(), listB.size());
// This would pass even if both lists point to the same object
```