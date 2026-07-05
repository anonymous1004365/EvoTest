---
name: throwable-proxy-class-loading-failure
description: When constructing ThrowableProxy for a Throwable whose stack trace contains
  classes that cannot be loaded (NoClassDefFoundError), the proxy should not propagate
  the linkage error. Test with an exception whose stack trace includes a class that
  exists but cannot be loaded by the caller's class loader.
code_tags:
- NULL_CHECK
- CLASS_LOADING_FAILURE
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# throwable-proxy-class-loading-failure

## Instructions

# ThrowableProxy Class Loading Failure Handling

## Instructions

- WHEN the TG encounters code in `ThrowableProxy` (or similar proxy/wrapper code) that calls `Loader.loadClass()` or `ClassLoader.loadClass()` to resolve class names from a `Throwable`'s stack trace elements
- THEN the TG should write a test that constructs an exception whose stack trace contains a class reference that triggers `NoClassDefFoundError` when the proxy attempts to load the class — specifically, the test should:
  1. Create a `Throwable` whose `StackTraceElement` array includes a class that the caller's `ClassLoader` cannot resolve (e.g., a class that was loaded by a different class loader and is not visible)
  2. Pass that `Throwable` to the `ThrowableProxy` constructor
  3. Verify that the `ThrowableProxy` is constructed successfully WITHOUT throwing a `NoClassDefFoundError` or any other `LinkageError`
  4. Verify the resulting proxy object is non-null and contains the expected number of stack trace elements (matching the original throwable's stack trace depth, even for unloadable frames)
  5. Expect that the test FAILS on the buggy version with a `NoClassDefFoundError` (or similar linkage error), and PASSES on the fixed version where the error is caught and the proxy gracefully handles the unloadable class

- Common pitfalls to avoid:
  - Testing only with normal exceptions whose stack trace classes are all loadable — this misses the bug entirely
  - Using `ClassNotFoundException` instead of `NoClassDefFoundError` — the bug is specifically about linkage errors (subclasses of `LinkageError`), not checked exceptions
  - Assuming all classes on the stack trace are loaded by the same class loader that the proxy uses — the fix involves catching `Throwable` or `LinkageError` during class loading

### Correct test approach (what to do):

```java
// Create a throwable whose stack trace contains a class not loadable by the current class loader
// Use a mechanism like a custom ClassLoader or an unloadable inner class reference
Throwable throwable;
try {
    // Trigger an exception in a context where the throwing class
    // is only visible to a different class loader
    throw new SomeException();
} catch (SomeException e) {
    throwable = e;
}
// Now construct ThrowableProxy with this throwable
ThrowableProxy proxy = new ThrowableProxy(throwable);
// Verify it succeeded - proxy should not be null
assertNotNull(proxy);
// Verify stack trace elements are preserved
assertEquals(throwable.getStackTrace().length, proxy.getStackTraceProxyArray().length);
```

### Incorrect test approach (common mistake):

```java
// WRONG: Testing only with normal exceptions
ThrowableProxy proxy = new ThrowableProxy(new RuntimeException("test"));
assertNotNull(proxy);
// This passes on both buggy and fixed versions, missing the bug
```