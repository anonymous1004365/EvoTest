---
name: blob-reference-count-on-serialize
description: When testing serialization of Blob subclasses (like custom inline ReferencedBlob
  implementations), verify that the reference counting counts correctly after serialization/deserialization
  round-trips. The reference count should be 0 (zero) for the deserialized blob reference,
  not 1.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# blob-reference-count-on-serialize

## Instructions

# Blob Reference Count After Serialization

## Instructions

WHEN the TG encounters a test that creates custom inline Blob subclasses (e.g., extending `ArrayBasedBlob`) and serializes/deserializes them via a `BlobSerializer` chain (like a `BlobIdSerializer` wrapped around a `Base64BlobSerializer`), THEN it should verify that the reference count of the deserialized blob is correctly handled.

- Specifically, after serializing a blob (e.g., a `ReferencedBlob` extending `ArrayBasedBlob`) and then deserializing it back, call `((ReferencedBlob) deserializedBlob).getReferenceCount()` and assert that it returns `0` (zero), not `1`.
- The test should create a `BlobSerializer` chain: `new BlobIdSerializer(new Base64BlobSerializer())`.
- Pass the blob to `blobSerializer.serialize(blob)` to get a key, then use `blobSerializer.deserialize(key)` to get the deserialized blob.
- Cast the result back to the specific subclass type before calling `getReferenceCount()`.
- Common pitfall: Testing only that serialization/deserialization round-trips the content correctly (e.g., comparing byte arrays) without checking internal state like reference counts. The reference count must be validated as part of the state test because it tracks lifecycle management (whether the blob store is still referencing the blob's content).
- Another common pitfall: Assuming all serializer implementations handle reference counting the same way — this test specifically targets the interaction between `BlobIdSerializer` and `Base64BlobSerializer` used together, where a bug causes the reference count to be wrong after deserialization.

### Example (correct approach):
```java
// Create serializer chain
BlobSerializer blobSerializer = new BlobIdSerializer(new Base64BlobSerializer());

// Create a blob with content
byte[] content = "test".getBytes();
ReferencedBlob blob = new ReferencedBlob(content, 1L);

// Serialize
String id = blobSerializer.serialize(blob);

// Deserialize
Blob result = blobSerializer.deserialize(id);

// Verify reference count is 0 (not 1)
assertEquals(0, ((ReferencedBlob) result).getReferenceCount()); // Passes on fixed version
```

### Example (incorrect approach — missing state validation):
```java
BlobSerializer blobSerializer = new BlobIdSerializer(new Base64BlobSerializer());
ReferencedBlob blob = new ReferencedBlob("test".getBytes(), 1L);
String id = blobSerializer.serialize(blob);
Blob result = blobSerializer.deserialize(id);
// BUG: Only comparing byte content — missing reference count assertion
assertArrayEquals(blob.getNewBinary().getBytes(), result.getNewBinary().getBytes());
// The test passes on both buggy and fixed versions because content is correct,
// but fails to catch the reference count bug!
```