---
name: reattach-versioned-page-deserialization
description: When testing page versioning with deserialization/reattachment, test
  that re-attaching a page after deserialization restores its internal versioning
  state correctly. This prevents StaleVersionException on subsequent detach calls.
code_tags:
- VERSIONING_STATE
test_pattern: STATE_TEST
---

# reattach-versioned-page-deserialization

## Instructions

# Reattach Versioned Page After Deserialization

## Instructions

- WHEN the TG encounters a component system that supports page versioning with `Page#internalAttach()` and `Page#internalDetach()` methods, and components can be serialized/deserialized,
- THEN the TG should create a test that:
  1. Creates a page and adds it to a page map with version management (e.g., `UndoPageVersionManager`).
  2. Calls `page.internalDetach()` to simulate the page being used and versioned.
  3. Serializes the page to a byte array and deserializes it back (simulating loading from a persisted state).
  4. After deserialization, calls `(page).internalAttach(pageMap)` to re-attach the page to the page map.
  5. Verifies that `page.getVersionManager().getVersion()` returns the correct version number (e.g., 1), NOT the initial value (e.g., 0).
  6. Optionally, calls `internalDetach()` again on the re-attached page and verifies that no exception (e.g., `StaleVersionException`) is thrown, confirming that the version manager state is consistent after reattachment.
- Common pitfalls: 
  - Testing only that a page can be serialized and deserialized without checking that its versioning state (the current version number) survives the round-trip.
  - Forgetting to actually call `internalDetach()` before serialization, which is what increments the version and creates the state that must be restored.
  - Calling `internalAttach()` without passing the correct `pageMap` argument, as the reattach logic may need the original page map to restore the version manager.
  - Assuming that the default constructor or default version manager state is correct after deserialization.

### Correct example (from ReattachVersioningTest.testReattach):
```java
// Create page and add to page map with version manager
pageMap.put(page);
page.internalDetach();

// Serialize and deserialize
byte[] data = SerializationUtils.serialize(page);
page = (ReattachTestPage) SerializationUtils.deserialize(data);

// Re-attach to page map
page.internalAttach(pageMap);

// Verify version state is restored
assertEquals(1, page.getVersionManager().getVersion());

// Verify no exception on subsequent detach
page.internalDetach();
```

### Incorrect example (what would miss the bug):
```java
// Create page and add to page map
pageMap.put(page);

// Serialize and deserialize without detaching first
byte[] data = SerializationUtils.serialize(page);
page = (ReattachTestPage) SerializationUtils.deserialize(data);

// Re-attach
page.internalAttach(pageMap);

// Only check that version is 0 (initial), missing the fact that the version
// state was lost during deserialization
assertEquals(0, page.getVersionManager().getVersion());
```