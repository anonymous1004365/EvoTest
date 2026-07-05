---
name: writable-serialization-roundtrip-for-iterator-settings
description: When testing mapred/mapreduce classes that implement Writable, always
  test round-trip serialization for all fields including iterators. This skill catches
  bugs where iterators set via setIterators() are lost or returned as null after write()/readFields()
  deserialization.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# writable-serialization-roundtrip-for-iterator-settings

## Instructions

# Writable Serialization Round-Trip for IteratorSettings

## Instructions

- WHEN the TG encounters a class that implements `org.apache.hadoop.io.Writable` (e.g., `RangeInputSplit`) that has a method `setIterators(List<IteratorSetting>)` and `getIterators()`, and the test performs a `write()` followed by `readFields()` on a `DataOutput`/`DataInput` stream
  - THEN the TG should verify that **all** fields survive the serialize-deserialize round trip, especially collection fields like iterators
  - Create a Writable implementation (or use the existing one), set one or more `IteratorSetting` objects on it via `setIterators()`, serialize it with `write(DataOutput)`, deserialize it with `readFields(DataInput)` into a new instance, then compare the post-deserialization state with the original state
  - Assert that `getIterators()` returns a non-null, non-empty list containing the expected `IteratorSetting` objects with correct `name`, `priority`, `iteratorClass`, and `properties` after round-trip

- Common mistakes to avoid:
  - Testing only primitive/String fields but not testing collection/iterator fields after serialization
  - Forgetting that `Writable` serialization may omit fields if not properly implemented in `write()`/`readFields()`, leading to `null` after deserialization
  - Not verifying that the iterators list is non-null after deserialization (only checking the original object's state)
  - Using a single `RangeInputSplit` instance for both write and read without creating a separate deserialization target instance

- Examples:

  **Correct test pattern:**
  ```java
  // Create original split, populate iterators
  RangeInputSplit split = new RangeInputSplit("table", "id", ...);
  List<IteratorSetting> iterators = new ArrayList<>();
  IteratorSetting is1 = new IteratorSetting(50, "SummingCombiner",
      "org.apache.accumulo.core.iterators.user.SummingCombiner");
  is1.addOption("foo", "bar");
  iterators.add(is1);
  IteratorSetting is2 = new IteratorSetting(100, "WholeRowIterator",
      "org.apache.accumulo.core.iterators.user.WholeRowIterator");
  is2.addOption("bar", "foo");
  iterators.add(is2);
  split.setIterators(iterators);
  
  // Round-trip serialize
  ByteArrayOutputStream baos = new ByteArrayOutputStream();
  DataOutputStream out = new DataOutputStream(baos);
  split.write(out);
  out.close();
  
  RangeInputSplit split2 = new RangeInputSplit();
  ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
  DataInputStream in = new DataInputStream(bais);
  split2.readFields(in);
  in.close();
  
  // Assert iterators survived
  assertNotNull("Iterators should not be null after deserialization", split2.getIterators());
  assertEquals(2, split2.getIterators().size());
  assertEquals("SummingCombiner", split2.getIterators().get(0).getName());
  assertEquals("WholeRowIterator", split2.getIterators().get(1).getName());
  ```

  **Incorrect test pattern (will miss the bug):**
  ```java
  RangeInputSplit split = new RangeInputSplit("table", ...);
  split.setIterators(someIterators);
  // Only checks pre-serialization state
  assertNotNull(split.getIterators());
  // Never serializes and deserializes to verify the field survives
  ```