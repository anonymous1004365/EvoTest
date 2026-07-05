---
name: template-parameter-type-validation
description: When validating proxy template parameters to prevent stack introspection errors, test with types that throw during class initialization to verify the system handles class loading failures gracefully.
code_tags: ['ARGUMENT_VALIDATION', 'ARRAY_ITERATION', 'NULL_CHECK', 'EXCEPTION_HANDLING', 'STATE_MUTATION']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Introspecting Stack Traces with Classes That Cannot Initialize

## Instructions

- WHEN the code under test wraps a `Throwable` (e.g., `ThrowableProxy`), and the stack trace contains a frame whose declaring class throws during static initialization (e.g., a class with a `static` block that unconditionally throws an `Error`), THEN the test must verify that stack introspection does NOT itself throw an `Error` / `NoClassDefFoundError`.  

- WHEN the Throwable's stack trace includes frames referencing a class that fails to initialize (e.g., `AlwaysThrowsError` whose `static { if (true) { throw new Error(...); } }`), THEN the test must catch the original `Throwable`, pass it to the proxy-building logic (e.g., `new ThrowableProxy(e)` or `logger.error(e.getMessage(), e)`), and assert that *no secondary exception is thrown* from the introspection code itself.

- The test should NOT merely verify the original exception is caught; it must specifically verify that the *stack trace processing* in the proxy does not fail. Use a try-catch around the proxy/logging call and `fail()` if an unexpected exception propagates.

- **Common pitfall**: Testing only with ordinary exceptions like `IOException` or `NullPointerException`, which do NOT trigger class-loading failures. The bug only appears when a stack frame's class throws an `Error` during `static` initialization or class loading.

- **Concrete example** (correct):
```java
public static class AlwaysThrowsError {
    static {
        if (true) {
            throw new Error("I always throw an Error when initialized");
        }
    }
}

@Test
public void testLogStackTraceWithClassThatCannotInitialize() {
    try {
        new AlwaysThrowsError();
        fail("Expected Error from static initializer");
    } catch (final Throwable e) {
        Logger logger = LogManager.getLogger(getClass());
        // This must NOT throw: the proxy must handle classes that fail loading
        logger.error(e.getMessage(), e);
        logger.error(e);
    }
}
```

- **Concrete example** (incorrect — misses the bug):
```java
@Test
public void testLogStackTraceWithNormalException() {
    // Only tests with a normal IOException — won't catch the class-loading bug
    ThrowableProxy proxy = new ThrowableProxy(new IOException("test"));
    // This passes even on the buggy version
}
```

- WHEN writing such a test, ensure the class that cannot initialize is a **public static inner class** (or a top-level class) in the test class, so that its stack trace frame appears when the Error propagates through the test method. The key is that the class's *declaring frame* is in the stack trace being processed.