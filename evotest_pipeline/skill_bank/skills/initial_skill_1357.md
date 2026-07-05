---
name: circular-throwable-cause-protection
description: When constructing ThrowableProxy wrappers for throwables that may have
  circular cause/suppressed exception chains, tests must verify that StackOverflowError
  is avoided by creating a throwable with a self-referencing cause chain.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# circular-throwable-cause-protection

## Instructions

# Circular Throwable Cause Protection

## Instructions

- WHEN the TG encounters a class that wraps Throwable instances (like `ThrowableProxy`) — especially one that recursively traverses `getCause()`, `getSuppressed()`, or similar methods to build a proxy object graph
- THEN it should write a test that creates a throwable with a **circular cause chain** (e.g., `Throwable a = new Throwable(); Throwable b = new Throwable(a); a.initCause(b);`) and verifies that constructing the wrapper does **not** throw a `StackOverflowError`
- The test should pass on the fixed version and would have failed (hit infinite recursion) on the buggy version

### Concrete guidance for `ThrowableProxy`

- Use `Throwable.initCause()` to create a circular reference: create `Throwable cause1 = new Throwable("cause1")`, then `Throwable cause2 = new Throwable("cause2", cause1)`, then `cause1.initCause(cause2)` — this forms a cycle where `cause1 -> cause2 -> cause1`
- Construct `new ThrowableProxy(cause1)` inside a `try` block and call a method that materializes the proxy chain (e.g., throwableProxy.toString())
- Expect the construction to complete without a `StackOverflowError`
- **Common pitfall**: Only testing linear cause chains (A -> B -> C) without cycles. The bug only manifests when causes reference each other, creating an infinite loop during proxy construction.
- **Common pitfall**: Forgetting to check suppressed exception cycles as well — circular suppressed chains can also cause `StackOverflowError`.

### Example (correct) pattern

```java
@Test
public void testCircularCauseExceptions() {
    // Create a circular cause chain
    Throwable cause1 = new Throwable("cause1");
    Throwable cause2 = new Throwable("cause2", cause1);
    cause1.initCause(cause2);  // now cause1 -> cause2 -> cause1
    
    try {
        // This should NOT throw StackOverflowError
        ThrowableProxy proxy = new ThrowableProxy(cause1);
        // Also trigger proxy materialization
        proxy.toString();
    } catch (StackOverflowError e) {
        fail("StackOverflowError due to circular cause references: " + e.getMessage());
    }
}
```

### Example (incorrect) pattern

```java
// ❌ BAD: Only tests linear chains, misses the circular case
@Test
public void testCauseChain() {
    Throwable a = new Throwable("a");
    Throwable b = new Throwable("b", a);
    // Linear chain: a -> b, no cycle
    ThrowableProxy proxy = new ThrowableProxy(b);
    // This test passes even on buggy version, missing the real issue
}
```

### What to verify

- The test should verify that the `ThrowableProxy` constructor (or equivalent recursive traversal logic) completes without infinite recursion
- If the method handles suppressed exceptions (via `getSuppressed()`), also test circular suppressed chains by adding a throwable as its own suppressed exception with `addSuppressed()`
- On the buggy version, the test would throw `StackOverflowError`; on the fixed version it should complete normally