---
name: serialization-roundtrip-exact-bytes
description: When implementing Writable interface for custom serialization, verify
  that after serializing an object and deserializing it, the input stream has exactly
  zero bytes remaining. This detects write/read asymmetry bugs where the number of
  bytes written doesn't match what's read.
code_tags:
- SERIALIZATION_DESERIALIZATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# serialization-roundtrip-exact-bytes

## Instructions

# Serialization Roundtrip Must Read Exactly Written Bytes

## Instructions

- WHEN the TG encounters a class implementing `Writable` (or similar serialization interface) with custom `write(DataOutput)` and `readFields(DataInput)` methods
  - THEN the TG should create a roundtrip serialization test that:
    1. Creates an instance with specific field values
    2. Serializes it to a `ByteArrayOutputStream` via `ObjectOutputStream`
    3. Deserializes into a fresh instance via `ObjectInputStream`
    4. Asserts that `bais.available() == 0` after deserialization completes
    5. Compares all fields between original and deserialized objects
  - Common pitfalls to avoid:
    - Testing only non-null fields without testing null/empty cases
    - Failing to verify the stream is fully consumed (extra bytes = write/read asymmetry)
    - Not testing with `null` value for fields that could be null (e.g., `FileSplit.getLocations()` can return null)
    - Not testing with both empty and populated arrays/collections

- WHEN the `write(DataOutput)` method writes fields in a certain order and `readFields(DataInput)` reads them back
  - THEN the test MUST ensure the number and types of fields written exactly match what is read, byte-for-byte
  - Common pitfalls to avoid:
    - The write method writes an array directly via `fileSplit.write(out)` while readFields reconstructs the FileSplit from individual fields — this mismatch can cause extra bytes or missed data

- WHEN a writable class contains a field that holds an array (e.g., `String[]` hosts from `FileSplit.getLocations()`)
  - AND that field can potentially be `null`
  - THEN the test must include a case where the array is `null` to verify proper null handling during serialization
  - Common pitfalls to avoid:
    - Writing `hosts.length` without a null check (causes NullPointerException during write)
    - Reading without checking for a sentinel/null flag (causes IndexOutOfBoundsException or wrong data during read)

**Correct example**: The `WikipediaInputSplit` buggy version writes `hosts.length` directly without null-checking, and reads `in.readInt()` to get the count without a null flag. The fixed version uses `out.writeBoolean(hosts == null)` / `in.readBoolean()` to handle null gracefully.

**Incorrect example**: Writing `out.writeInt(hosts.length)` when `hosts` could be null, or reading `in.readInt()` to determine array size without first checking a sentinel boolean.