---
name: serialization-roundtrip-nested-throwable
description: When a ThrowableProxy (or any serializable proxy/wrapper) is serialized
  and deserialized, the deserialized copy may have null internal fields (e.g., this.proxy
  cause) leading to NullPointerException when calling methods like getExtendedStackTraceAsString.
  The TG should test serialization round-trips on objects with nested structures (causes,
  suppressed exceptions).
code_tags:
- NULL_CHECK
- SERIALIZATION_BUFFER_MGMT
test_pattern: STATE_TEST
---

# serialization-roundtrip-nested-throwable

## Instructions

# Serialization Round-Trip of ThrowableProxy with Nested Causes

## Instructions

- WHEN the TG encounters a class that wraps a `Throwable` and implements `Serializable` (e.g., `ThrowableProxy`), and the class stores internally a reference to another instance of itself as a "cause" field
- THEN the TG should write a test that:
  1. Creates a deep/nested throwable chain (e.g., `new Exception("level2", new Exception("level1"))`) — not just a flat throwable
  2. Constructs the proxy from the nested throwable
  3. Serializes the proxy using standard Java serialization (e.g., `ObjectOutputStream` with `ByteArrayOutputStream`)
  4. Deserializes it back using `ObjectInputStream`
  5. Invokes a method that traverses internal proxy fields (e.g., `getExtendedStackTraceAsString(Strings.EMPTY)`) and verifies it does NOT throw `NullPointerException`
  6. Asserts the deserialized output matches the original

- Common pitfalls to avoid:
  - Testing serialization only of flat (non-nested) proxies, which may not trigger the lazy-initialization or null-field code paths
  - Only comparing the `toString()` of original and deserialized objects (which may itself trigger internal state initialization), instead of testing a method that directly accesses internal proxy fields
  - Not catching the case where the deserialized proxy has a `null` cause reference that only throws NPE when traversed by `getExtendedStackTrace`, `getRootCause`, or similar methods

- Example (correct):
```java
@Test
public void testSerialization_getExtendedStackTraceAsStringWithNestedThrowableDepth1() throws Exception {
    Throwable throwable = new Exception("depth2", new Exception("depth1"));
    ThrowableProxy proxy = new ThrowableProxy(throwable);
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(bos);
    oos.writeObject(proxy);
    oos.flush();
    oos.close();
    ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bis);
    ThrowableProxy proxy2 = (ThrowableProxy) ois.readObject();
    assertEquals(proxy.getExtendedStackTraceAsString(Strings.EMPTY), proxy2.getExtendedStackTraceAsString(Strings.EMPTY));
}
```

- Example (incorrect — flat only, no nested cause):
```java
@Test
public void testSerialization_basic() throws Exception {
    Throwable throwable = new Exception("flat");
    ThrowableProxy proxy = new ThrowableProxy(throwable);
    // serialize and deserialize...
    // This passes on buggy code because no nested cause is traversed
    // It does NOT detect the NPE bug
}
```