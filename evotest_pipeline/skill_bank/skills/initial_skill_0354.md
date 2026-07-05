---
name: serialization-reconstructs-transient-state
description: When a class implements Serializable but has transient fields that hold
  critical internal state, the test must verify that serialization round-trip correctly
  reconstructs the internal state, and that subsequent operations (put/get, iteration)
  succeed without NullPointerException.
code_tags:
- CHILD_ADDITION_REPLACE
- CHILD_REMOVAL_TRACKING
- NULL_CHECK
test_pattern: STATE_TEST
---

# serialization-reconstructs-transient-state

## Instructions

# Serialization Must Reconstruct Transient Internal State

## Instructions

- WHEN the TG encounters a class that implements `Serializable` and has `transient` fields that store critical internal state (such as an `Entry<V>[] table`, `int size`, or `AtomicInteger modCount` for a hash map, or any data structure with manually managed transient arrays/counters)
- THEN the TG MUST write a test that serializes an instance with populated data (e.g., put entries into a map), deserializes it, and verifies that the deserialized instance is fully functional — not just that the object is non-null, but that:
  1. Data retrieved from the deserialized object matches the original data (e.g., `deserialized.get(key)` returns the correct value)
  2. The deserialized object can be mutated without throwing `NullPointerException` (e.g., `deserialized.put(newKey, newValue)`)
  3. The deserialized object supports collection-view operations (e.g., `deserialized.entrySet().iterator()`) without throwing `NullPointerException`
- The test should use `ObjectOutputStream` / `ObjectInputStream` with a `ByteArrayOutputStream` / `ByteArrayInputStream` round-trip
- Common pitfalls:
  - ❌ Testing only that the deserialized object is not null — this misses broken transient state
  - ❌ Testing only that `get()` works after deserialization — this can pass even when other internal state is broken (e.g., `modCount` lost, causing `ConcurrentModificationException` on iteration)
  - ❌ Forgetting to test mutation after deserialization (`put`, `remove`) — this catches broken internal structures like uninitialized tables
  - ❌ Forgetting to test collection views (e.g., `entrySet().iterator()`, `keySet()`, `values()`) — these may fail independently if `modCount` or other transient tracking fields are not restored
- Correct example for `IntHashMap<V>`:
  ```java
  IntHashMap<String> map = new IntHashMap<>();
  map.put(1, "one");
  map.put(2, "two");

  ByteArrayOutputStream baos = new ByteArrayOutputStream();
  ObjectOutputStream oos = new ObjectOutputStream(baos);
  oos.writeObject(map);

  byte[] serialized = baos.toByteArray();
  ByteArrayInputStream bais = new ByteArrayInputStream(serialized);
  ObjectInputStream ois = new ObjectInputStream(bais);
  IntHashMap<String> deserialized = (IntHashMap<String>) ois.readObject();

  // Verify data survived
  assertThat(deserialized.get(1), is(equalTo("one")));
  assertThat(deserialized.get(2), is(equalTo("two")));

  // Verify mutation after deserialization (catches broken internal table)
  deserialized.put(3, "three");

  // Verify collection views after deserialization (catches broken modCount)
  deserialized.entrySet().iterator();
  ```
- Incorrect example (too weak):
  ```java
  IntHashMap<String> deserialized = (IntHashMap<String>) ois.readObject();
  assertNotNull(deserialized); // WRONG: passes even when internal state is lost
  // Missing: data retrieval, mutation, iteration checks
  ```