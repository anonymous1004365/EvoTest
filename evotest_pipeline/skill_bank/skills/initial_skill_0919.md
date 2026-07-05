---
name: writable-field-roundtrip-consistency
description: When implementing Writable interface serialization, test that all non-transient
  fields survive a full write/read roundtrip. This is essential when fields are conditionally
  serialized (with null-guards in write and presence-flags in read), because the write
  and read must agree on field count, order, and conditions.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# writable-field-roundtrip-consistency

## Instructions

# Writable Field Roundtrip Consistency

## Instructions

WHEN a class implements `Writable` (or `Serializable`) and has multiple optional/conditional fields — especially fields serialized with a `null` check before writing (e.g., `out.writeBoolean(null != field)`) and read with a presence flag (e.g., `if (in.readBoolean())`) — THEN the test MUST verify that the `write()` and `readFields()` methods handle field order and conditional logic consistently for ALL fields.

- Specifically, the test must:
  1. Create a fully populated instance (set ALL fields to non-null/non-default values).
  2. Call `write()` to serialize to a `ByteArrayOutputStream`/`DataOutputStream`.
  3. Create a fresh instance using the default constructor.
  4. Call `readFields()` from a `ByteArrayInputStream`/`DataInputStream` constructed from the serialized bytes.
  5. Assert that EVERY set field in the original equals the corresponding field in the deserialized instance.

- When the bug is "expected:<value> but was:<null>" for a particular field (e.g., `table`), this indicates that the `write()` method serialized the field but `readFields()` did not read it back (or read it in the wrong order). The test must catch such mismatches.

- Do NOT test only a subset of fields — test every non-transient field that can be populated. If a field is conditionally serialized, test with both null and non-null values.

- Common pitfalls:
  - Forgetting to test fields that were added after the initial implementation (regression risk)
  - Testing only simple fields (like `Range` and `locations`) and ignoring token, auths, iterators, log level, etc.
  - Assuming that if `write()` and `readFields()` compile, they agree on field format and order
  - Using the same object for both write and read (must use separate instances)

### Correct Example (catches the bug):
```java
// Create a fully populated split
RangeInputSplit split = new RangeInputSplit(new Range(new Key("a"), new Key("b")), new String[]{"localhost"});
split.setTable("table");
split.setAuths(new Authorizations("foo"));
split.setOffline(true);
split.setIsolatedScan(true);
split.setUsesLocalIterators(true);
split.setFetchedColumns(fetchedColumns);
split.setToken(new PasswordToken("password"));
split.setPrincipal("root");
split.setInstanceName("instance");
split.setMockInstance(true);
split.setZooKeepers("localhost");
split.setIterators(iterators);
split.setLogLevel(Level.WARN);

// Serialize
ByteArrayOutputStream baos = new ByteArrayOutputStream();
DataOutputStream dos = new DataOutputStream(baos);
split.write(dos);

// Deserialize into fresh instance
RangeInputSplit newSplit = new RangeInputSplit();
ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
DataInputStream dis = new DataInputStream(bais);
newSplit.readFields(dis);

// Assert ALL fields
Assert.assertEquals(split.getTable(), newSplit.getTable());       // FAILS on buggy version
Assert.assertEquals(split.getAuths(), newSplit.getAuths());
Assert.assertEquals(split.isOffline(), newSplit.isOffline());
Assert.assertEquals(split.getToken(), newSplit.getToken());
Assert.assertEquals(split.getPrincipal(), newSplit.getPrincipal());
// ... etc for every field
```

### Incorrect Example (misses the bug):
```java
// Only tests Range and locations — does NOT catch table serialization bug
RangeInputSplit split = new RangeInputSplit(new Range(new Key("a"), new Key("b")), new String[]{"localhost"});
ByteArrayOutputStream baos = new ByteArrayOutputStream();
DataOutputStream dos = new DataOutputStream(baos);
split.write(dos);
RangeInputSplit newSplit = new RangeInputSplit();
newSplit.readFields(new DataInputStream(new ByteArrayInputStream(baos.toByteArray())));
Assert.assertEquals(split.getRange(), newSplit.getRange());      // PASSES but doesn't test 'table'
Assert.assertArrayEquals(split.getLocations(), newSplit.getLocations());  // PASSES but doesn't test 'table'
```