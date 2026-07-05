---
name: double-initialization-guard
description: When a component provides an initialization method (e.g., init, setup,
  start) that should only be called once, test that calling it a second time does
  not corrupt state or throw unexpected exceptions. This applies to instances where
  initialization sets up cryptographic keys, shared resources, or protocol-specific
  state.
code_tags:
- STATE_MUTATION
- INITIALIZATION_ORDER
test_pattern: STATE_TEST
---

# double-initialization-guard

## Instructions

# Double-Initialization Guard

## Instructions

- WHEN the TG encounters a class with a public initialization method (e.g., `init`, `start`, `setup`) that sets up internal state such as cryptographic keys, shared data structures, or protocol connections
- THEN the TG should write a test that calls the initialization method **twice** in sequence on the same object instance, verifying that the second call either:
  - (a) is idempotent (produces the same state as after the first call), OR
  - (b) throws a specific documented exception (e.g., `IllegalStateException` with the message "already initialized"),
- **Crucially**, the test must verify that after the second initialization call, the object's internal state is still valid and functional — not corrupted (e.g., key material still decrypts, resources are not leaked, protocol operations still succeed).
- **Common pitfalls**:
  - Testing only that the first initialization works, and never exercising a second call to the same method.
  - Assuming that re-initialization will throw an exception without verifying *what* exception is thrown and that the object remains usable afterward.
  - Forgetting to check internal/secret state (e.g., keys, nonces, session data) after double-init — it may silently become null or inconsistent even if no exception is thrown.

**Correct example** (idempotent init):
```java
@Test
public void testDoubleInitDoesNotCorruptState() {
    MyProtocol protocol = new MyProtocol();
    protocol.init(keyMaterial);          // first init — succeeds
    protocol.init(keyMaterial);          // second init — must be safe
    // Verify internal state is still valid
    assertNotNull(protocol.getSecretKey());
    assertTrue(protocol.canProcessMessages());
}
```

**Correct example** (exception-throwing init):
```java
@Test(expected = IllegalStateException.class)
public void testDoubleInitThrows() {
    MyProtocol protocol = new MyProtocol();
    protocol.init(keyMaterial);          // first init — succeeds
    protocol.init(keyMaterial);          // second init — must throw
}
```
*(Also consider verifying that after catching the exception, the object is not in a broken state, e.g., `assertNotNull(protocol.getSecretKey())`.)*

**Incorrect example** (only tests single init — misses the double-init bug):
```java
@Test
public void testInit() {
    MyProtocol protocol = new MyProtocol();
    protocol.init(keyMaterial);
    assertNotNull(protocol.getSecretKey());  // Only tests single init
    // BUG: If init() were called again, the key could be overwritten or nullified
}
```