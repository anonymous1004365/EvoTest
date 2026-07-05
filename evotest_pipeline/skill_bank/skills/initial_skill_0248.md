---
name: serialized-throwableproxy-null-throwable-guard
description: When testing serialization/deserialization of ThrowableProxy, a deserialized
  proxy has throwable=null, so any method that accesses the transient 'throwable'
  field can NPE. Tests must invoke post-deserialization methods like getExtendedStackTraceAsString()
  on the deserialized proxy and expect NullPointerException or guard against it.
code_tags:
- STATE_MUTATION
- CONCURRENCY
- NULL_CHECK
- SERIALIZATION_DESERIALIZATION
test_pattern: EXCEPTION_TEST
---

# serialized-throwableproxy-null-throwable-guard

## Instructions

# ThrowableProxy Deserialization Null Throwable Handling

## Instructions

When the TG encounters a test for serialization/deserialization of `ThrowableProxy`, the deserialized proxy object will have its `transient Throwable throwable` field set to `null` (because it is transient and not serialized).

- WHEN the TG writes a test that serializes and then deserializes a `ThrowableProxy` instance (using `ObjectOutputStream`/`ObjectInputStream`)
- THEN the TG MUST test that methods accessing the `throwable` field on the deserialized proxy do not cause a `NullPointerException`
- Specifically, the TG MUST test `getExtendedStackTraceAsString(String suffix)` on the deserialized `ThrowableProxy` because this method internally accesses the `throwable` field (e.g., `throwable.getStackTrace()` or `throwable.getMessage()`) and will throw `NullPointerException` when `throwable` is null
- The TG MUST verify that calling `getExtendedStackTraceAsString()` (with any suffix or none) on a deserialized `ThrowableProxy` throws `NullPointerException` on the buggy version
- The TG MUST also check other methods that may access the `throwable` field after deserialization

**Common pitfalls to avoid:**
- Testing only that the proxy serializes/deserializes correctly without testing methods that access the `throwable` field
- Forgetting that `throwable` is `transient` and will be `null` after deserialization
- Testing only the `equals()`, `getName()`, `getMessage()`, or `getLocalizedMessage()` methods on the deserialized proxy without testing the methods that access the `throwable` field
- Assuming the deserialized object is fully functional just because its visible fields (name, message, etc.) are preserved

**Example (correct — catches the NullPointerException caused by accessing null throwable after deserialization):**

```java
@Test
public void testSerialization_getExtendedStackTraceAsString() throws Exception {
    ThrowableProxy proxy = new ThrowableProxy(new IOException("test"));
    byte[] binary;
    try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
         ObjectOutputStream oos = new ObjectOutputStream(bos)) {
        oos.writeObject(proxy);
        binary = bos.toByteArray();
    }
    ThrowableProxy proxy2;
    try (ByteArrayInputStream bis = new ByteArrayInputStream(binary);
         ObjectInputStream ois = new ObjectInputStream(bis)) {
        proxy2 = (ThrowableProxy) ois.readObject();
    }
    // This call throws NullPointerException on the buggy version because throwable is null after deserialization
    assertNull(proxy2.getExtendedStackTraceAsString(Strings.EMPTY));  // or expect NPE depending on the fix
}
```

**Example (incorrect — does not catch the bug):**

```java
@Test
public void testSerialization() throws Exception {
    ThrowableProxy proxy = new ThrowableProxy(new IOException("test"));
    byte[] binary = serialize(proxy);
    ThrowableProxy proxy2 = deserialize(binary);
    // Only checks the serialized fields — doesn't call any method accessing throwable
    assertEquals(proxy.getName(), proxy2.getName());
    assertEquals(proxy.getMessage(), proxy2.getMessage());
}
```