---
name: serialization-outside-application-lifecycle
description: When a class with custom serialization (writeObject/readObject) accesses
  external services (like IPageStore) during serialization, test that deserialization
  works correctly when those services are unavailable. This skill helps catch NullPointerExceptions
  and incorrect state after deserialization without expected application context.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# serialization-outside-application-lifecycle

## Instructions

# Serialization Outside Application Lifecycle

## Instructions

WHEN a class implements custom serialization (`writeObject`/`readObject`) that depends on external services (such as `IPageStore`, database connections, HTTP sessions, or other application-scoped services obtained via a static registry like `MANAGERS.get(applicationName)`), THEN test serialization and deserialization in the absence of those services to verify:

1. The object can be serialized to bytes without throwing a `NullPointerException`
2. The bytes can be deserialized back to an object without throwing a `NullPointerException`
3. The deserialized object is in a consistent state (not null, fields populated correctly)
4. The object can still function (e.g., methods like `getPage()` work) once the service is later re-provided

Concrete steps:

- WHEN the class looks up a service from a static `ConcurrentMap` (like `PageStoreManager.MANAGERS.get(applicationName)`) during `writeObject` or `readObject` which may return `null`,
  THEN set up the object with the service available, create a serialized byte array, then destroy/shut down the service, and attempt to deserialize from the bytes.
  - Verify deserialization succeeds without `NullPointerException`
  - Verify the deserialized object is non-null and its fields are intact (e.g., `applicationName`, `sessionId`)

- WHEN the class has an `afterReadObject` / deferred-conversion pattern (like `SessionEntry.convertAfterReadObjects()`),
  THEN verify that deserialization does NOT trigger the conversion (because the service is unavailable), or handles it gracefully without crashing.
  - Verify that the deserialized object can later be used after the service is re-registered (e.g., call `getPage()` after providing a new store)

- WHEN testing a class that implements `HttpSessionBindingListener` (like `SessionEntry`),
  THEN ensure that `valueUnbound` does not interfere with the serialization/deserialization test. Use `ThreadContext.detach()` before the test to clean up thread locals.

- Common pitfalls to avoid:
  - ❌ Testing only the happy path (service always available during deserialization)
  - ❌ Not verifying the deserialized object's state (assuming non-null means correct)
  - ❌ Forgetting that `readObject()` may trigger service lookups that return `null` outside the application lifecycle
  - ❌ Not asserting that `Application.exists()` returns `false` during the deserialization test

### Correct Example (from `PersistentPageManagerTest.serializationOutsideWicketLifecyle()`):

```java
@Test
public void serializationOutsideWicketLifecyle() throws IOException, ClassNotFoundException {
    // Arrange: clean thread locals
    ThreadContext.detach();

    // Arrange: create manager and store a page
    IPageManager pageManager = newPersistentPageManager(APP_NAME);
    TestPage toSerializePage = new TestPage();
    pageManager.touchPage(toSerializePage);
    pageManager.commitRequest();

    // Arrange: get the SessionEntry and destroy the manager (no IPageStore anymore)
    Serializable sessionEntry = pageManager.getContext().getSessionAttribute(null);
    pageManager.destroy();

    // Act: serialize (should work even without IPageStore)
    byte[] serializedSessionEntry = new JavaSerializer(APP_NAME).serialize(sessionEntry);
    assertNotNull("Must be able to serialize without store", serializedSessionEntry);

    // Act: deserialize (should work without Application/IPageStore)
    ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(serializedSessionEntry));
    assertFalse("Application should NOT exist during deserialization", Application.exists());
    assertEquals(APP_NAME, in.readObject());
    Serializable loadedSessionEntry = (Serializable) in.readObject();
    assertNotNull("Must be able to deserialize without store", loadedSessionEntry);

    // Act: re-provide the store and use the deserialized entry
    IPageManager newPageManager = newPersistentPageManager(APP_NAME);
    newPageManager.getContext().setSessionAttribute(null, loadedSessionEntry);

    TestPage deserializedPage = (TestPage) newPageManager.getPage(toSerializePage.getPageId());
    assertNotNull(deserializedPage);
    assertEquals(toSerializePage.instanceID, deserializedPage.instanceID);

    newPageManager.destroy();
}
```

### Incorrect Example (what to avoid):

```java
// ❌ WRONG: Only tests with the service available
@Test
public void testSerialization() {
    IPageManager pageManager = newPersistentPageManager(APP_NAME);
    Serializable sessionEntry = pageManager.getContext().getSessionAttribute(null);
    
    byte[] data = serialize(sessionEntry);
    Serializable result = deserialize(data);
    
    assertNotNull(result);  // This passes, but only because IPageStore was still registered
    // Does NOT test deserialization when Application is unavailable!
}
```