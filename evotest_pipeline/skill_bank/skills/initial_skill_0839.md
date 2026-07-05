---
name: proxy-exception-unwrapping
description: When testing code that uses java.lang.reflect.Proxy-based wrappers (like
  tracing or monitoring proxies), the TG must verify that original exceptions are
  propagated through InvocationTargetException unwrapping, not wrapped in it. This
  skill teaches how to test that checked exceptions thrown by proxied methods are
  correctly re-thrown as their original type.
code_tags:
- EXCEPTION_HANDLING
- ORDER_DEPENDENCY
test_pattern: EXCEPTION_TEST
---

# proxy-exception-unwrapping

## Instructions

# Proxy Exception Unwrapping Test Skill

## Instructions

- WHEN the TG encounters code that uses `java.lang.reflect.Proxy` with an `InvocationHandler` that catches `InvocationTargetException` and re-throws `ex.getCause()`, AND the proxied object's methods declare checked exceptions:
  - THEN the TG should write a test that:
    1. Creates a real object whose method throws a specific checked exception (e.g., `IOException`)
    2. Wraps it via the proxy mechanism (e.g., `TraceProxy.trace(callable)`)
    3. Calls the proxied method and asserts that the original exception type is thrown directly, NOT wrapped in `InvocationTargetException`
    4. Uses `@Test(expected = IOException.class)` (or the appropriate exception class) on the test method
  - The test should use `Callable<Object>` whose `call()` method declares `throws IOException`, and have it throw `new IOException()` inside.
  - The test should verify that `TraceProxy.trace(callable).call()` propagates the `IOException` without the caller needing to catch `InvocationTargetException` and unwrap it manually.

- WHEN the TG writes a test for exception propagation through proxy wrappers:
  - THEN the test must NOT catch `InvocationTargetException` and rethrow its cause — the proxy handler should already do this unwrapping.
  - The test should expect the original exception type (e.g., `IOException.class`) on the `@Test` annotation.
  - Verify that the exception message is preserved through the unwrapping.

- Common pitfalls to avoid:
  - ❌ Catching `InvocationTargetException` in the test and rethrowing `e.getCause()` — this masks the bug (the TG did this, and it's wrong because the proxy should already unwrap it).
  - ❌ Testing with a `Runnable` or a method that doesn't declare checked exceptions — only methods that declare `throws` with specific checked types expose the bug.
  - ❌ Assuming the proxy's exception handling is correct without testing it explicitly.

### Correct Example (what the test should look like):

```java
@Test(expected = IOException.class)
public void testTracedExceptionPropagation() throws Throwable {
    Callable<Object> callable = new Callable<Object>() {
        @Override
        public Object call() throws IOException {
            throw new IOException("test exception");
        }
    };
    TraceProxy.trace(callable).call();  // Should throw IOException directly, NOT InvocationTargetException
}
```

### Incorrect Example (what the buggy test looked like):

```java
// BUGGY TEST: Manually unwraps InvocationTargetException, hiding the proxy bug
@Test(expected = IOException.class)
public void testTracedException() throws Throwable {
    try {
        TraceProxy.trace(callable).call();
    } catch (InvocationTargetException e) {
        throw e.getCause();  // This unwraps it manually, but the proxy SHOULD do this
    }
}
```

### Key Insight

The failure message was: `expected<java.io.IOException> but was<java.lang.reflect.InvocationTargetException>`. This means `TraceProxy.trace(callable).call()` threw `InvocationTargetException` instead of `IOException`. The proxy's `InvocationHandler.invoke()` was supposed to catch `InvocationTargetException` and throw `ex.getCause()`, but it failed to do so. The test should be written to detect this by NOT manually unwrapping the exception.