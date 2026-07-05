---
name: throttler-jmx-exposed-state-type-mismatch
description: WHEN a class exposes internal state via JMX with a different return type
  than the internal field type (e.g., long vs int), THEN test that the JMX getter
  returns the expected (widened) type. This skill also applies when a setter passes
  a different type (e.g., long) to an internal setter that expects a narrower type
  (e.g., int).
code_tags:
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# throttler-jmx-exposed-state-type-mismatch

## Instructions

# Throttler JMX Exposed State Type Mismatch

## Instructions

- WHEN the test generator encounters a JMX-managed bean (a class annotated with `@ManagedResource`) that exposes internal state through getter/setter methods, AND the exposed JMX getter returns a type different from the internal processor's getter (e.g., ManagedThrottler.getMaximumRequestsPerPeriod() returns `long` while Throttler.getCurrentMaximumRequestsPerPeriod() returns `int`), THEN the test should:
  1. Call the JMX getter (via `mbeanServer.getAttribute(throttlerName, "MaximumRequestsPerPeriod")`) and verify the attribute is retrievable as the expected type (`Long`).
  2. Call the JMX setter with a `long` value (via `mbeanServer.setAttribute(throttlerName, new Attribute("MaximumRequestsPerPeriod", (long) value))`) and then read back the attribute to verify it was correctly set.
  3. Verify that after setting a value via JMX, the internal processor's matching getter (`getCurrentMaximumRequestsPerPeriod()` returning `int`) reflects the value — the widening conversion from `long` → `int` must work correctly and not cause unexpected behavior (e.g., truncation, loss of data).

- WHEN a JMX setter (`setAttribute`) receives a value of type `long` and delegates to a method that accepts a `long` parameter (e.g., `constant(maximumRequestsPerPeriod)` which takes `long`), THEN the test should verify that the value is correctly propagated through to the internal processor and is visible via JMX read-back. Do NOT assume that passing a `long` through an `Expression` pipeline preserves the value correctly without verifying.

- Common pitfalls to avoid:
  - **Pitfall**: Testing only via direct processor calls (e.g., `throttler.setMaximumRequestsPerPeriodExpression(...)`) without testing through the JMX layer. The bug may only manifest when values flow through the JMX MBean's `setAttribute` → `getAttribute` roundtrip.
  - **Pitfall**: Assuming that because `long` can hold an `int`, the widening conversion `int → long → int` is lossless. Test at boundaries (e.g., set `Integer.MAX_VALUE` via JMX and verify it comes back correctly).
  - **Pitfall**: Skipping verification that the JMX attribute is actually readable after being set. The managed bean's getter may not return the same conceptual value that was set (e.g., `getMaximumRequestsPerPeriod()` might return a cached or computed value different from what was set).

- Correct example (matching the ManagedThrottler case):
```java
// Set a new maximum requests per period via JMX
mbeanServer.setAttribute(throttlerName, new Attribute("MaximumRequestsPerPeriod", (long) 2));

// Verify the attribute was set by reading it back
Long period = (Long) mbeanServer.getAttribute(throttlerName, "MaximumRequestsPerPeriod");
assertNotNull(period);
assertEquals(2, period.longValue());
```

- Incorrect example (would miss the bug):
```java
// Only testing via direct processor call — does not exercise the JMX MBean roundtrip
throttler.setMaximumRequestsPerPeriodExpression(constant(2));
// Missing: verifying through JMX that the value is visible and correct
```