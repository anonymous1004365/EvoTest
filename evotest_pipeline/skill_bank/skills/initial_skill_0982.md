---
name: wrapper-processor-trace-label
description: When testing routes that use error handlers with traced processors that
  get wrapped, the TG should verify getTraceLabel() / toString() calls on wrapped
  processors return the wrapped processor's label, not the wrapper's Object.toString().
  Apply this skill when testing traceability of Camel processors that may be wrapped
  by other processor types.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- STRING_REPRESENTATION_IN_TEST
- TO_STRING_OVERRIDE
- WRAPPER_PROCESSOR_WRAPPING
test_pattern: STATE_TEST
---

# wrapper-processor-trace-label

## Instructions

# Wrapper Processor Trace Label Skill

## Instructions

- WHEN the TG encounters a test that involves a Camel `Processor` which is wrapped by another processor (e.g., `DefaultErrorHandler` wrapping `SendProcessor`, or any `Processor` wrapped via `ProcessorExchangeProcessorWrapper`), and the test checks the `getTraceLabel()` or `toString()` value of the wrapper
- THEN the TG should verify that the `getTraceLabel()` and `toString()` methods on the wrapper delegate correctly to the wrapped processor's `getTraceLabel()` implementation, rather than falling back to the default `Object.toString()` (which produces output like `wrap[org.apache.camel.processor.SendProcessor@1a2b3c]` instead of `ref:myProcessor`)
- The TG should write a test that:
  1. Creates a processor that implements `Traceable` (providing a meaningful `getTraceLabel()` like a processor ID or reference)
  2. Checks the `toString()` output on the wrapper does NOT include the wrapper's class name prefix like `wrap[...]` or default `Object.toString()` format (e.g., `className@hashCode`)
  3. If the framework exposes `getTraceLabel()` on the wrapper, assert that it returns the inner processor's label
- Common pitfalls:
  - Testing only the unwrapped processor's `getTraceLabel()` without testing through the wrapper — the bug may only appear after wrapping
  - Assuming `toString()` on a wrapper returns the same as `getTraceLabel()` on the inner processor — the wrapper may not override `toString()` properly
  - Not checking whether the wrapper forwards `getTraceLabel()` to the wrapped processor — some wrappers implement `Traceable` but return their own `toString()` instead of delegating

Example (correct):
```java
// When testing a wrapped processor's trace label
Processor myProcessor = new MyTraceableProcessor("myProcessor");
Processor wrapped = new SomeProcessorWrapper(myProcessor);
// Assert that getTraceLabel() returns the inner processor's label, not a default toString
assertEquals("myProcessor", wrapped.getTraceLabel());
```

Example (incorrect — won't catch the bug):
```java
// Only testing the inner processor directly
Processor myProcessor = new MyTraceableProcessor("myProcessor");
assertEquals("myProcessor", myProcessor.getTraceLabel());
// Missing the wrapper test — bug only appears when calling getTraceLabel() through the wrapper
```