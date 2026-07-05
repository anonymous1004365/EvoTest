---
name: deserialized-proxy-with-null-throwable
description: ''
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# deserialized-proxy-with-null-throwable

## Instructions

# Deserialized ThrowableProxy with Null Throwable

## Instructions

- WHEN the TG encounters code that formats a `LogEvent`'s throwable information (e.g. `ExtendedThrowablePatternConverter`, `ThrowablePatternConverter`, or any class that calls `event.getThrown()` and/or `event.getThrownProxy()`)
- THEN it should test a scenario where the LogEvent has:
  - `event.getThrown()` returning **null**
  - `event.getThrownProxy()` returning a **non-null** `ThrowableProxy` (constructed from a real `Throwable`)
  
  This simulates a deserialized LogEvent where the Throwable object is not available on the deserializing side, but the ThrowableProxy (which is serializable) carries all the stack trace information.
  
- **What to verify**: 
  - The formatter should NOT throw a `NullPointerException`.
  - The formatted output should still contain the throwable's message and stack trace elements (e.g. `originalThrowable.getMessage()`, the method name from `originalThrowable.getStackTrace()[0].getMethodName()`).
  
- **How to construct the test event**:
  ```java
  final Throwable originalThrowable = new Exception("something bad happened");
  final ThrowableProxy throwableProxy = new ThrowableProxy(originalThrowable);
  final Throwable deserializedThrowable = null;
  final Log4jLogEvent event = Log4jLogEvent.newBuilder()
          .setLoggerName("testLogger")
          .setLoggerFqcn(this.getClass().getName())
          .setLevel(Level.DEBUG)
          .setMessage(new SimpleMessage(""))
          .setThrown(deserializedThrowable)
          .setThrownProxy(throwableProxy)
          .setTimeMillis(0)
          .build();
  ```

- **Common pitfalls**:
  - Testing only the case where both `getThrown()` and `getThrownProxy()` are null — this misses the deserialization scenario.
  - Testing only the case where `getThrown()` is non-null — this is the happy path but doesn't cover the deserialized proxy case.
  - Assuming that a non-null `ThrowableProxy` implies a non-null `throwable` field inside the proxy — after deserialization, the proxy's `throwable` field (which is `transient`) will be null.
  - Not checking that the formatted output contains the original throwable's message and stack frames — the test should verify the content, not just the absence of exceptions.