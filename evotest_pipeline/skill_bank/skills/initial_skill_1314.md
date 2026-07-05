---
name: microservice-factory-description-overwrite
description: When creating Microservice instances from Map data, the description field
  can be overwritten to null by non-String values. This skill teaches how to test
  that setter methods properly validate and filter incoming data before applying state
  changes.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# microservice-factory-description-overwrite

## Instructions

# MicroserviceFactory Description Overwrite Bug

## Instructions

- WHEN the TG encounters a `MicroserviceFactory` class that creates `Microservice` objects from a `Map<String, Object>` (or similar key-value data), specifically a method like `createMicroservice` that iterates over map entries and calls setter methods (e.g., `setDescription`)
- THEN the TG should test that non-String value types in the map do NOT corrupt object state. In particular:
  - WHEN a map entry has key `"description"` with a non-String value (e.g., a `CtTypeReference` or any `Object` that is not a `String`)
  - THEN verify that `microservice.setDescription()` is either never called with the non-String value, OR that the setter filters non-String values gracefully
  - The test must verify that the description field remains unchanged (or null) rather than being set to an unexpected type's string representation
  - Use `assertNull(microservice.getDescription())` or an equivalent assertion to confirm no spurious non-String description was set

- Common pitfalls to avoid:
  - ❌ Testing only with `String` type map values — this masks the bug because the issue only appears with non-String values (e.g., `CtTypeReference`, `Integer`, custom objects)
  - ❌ Assuming `toString()` is called implicitly — verify explicitly that no unexpected object type becomes the description value
  - ❌ Not testing the interaction between the map iterator and the setter — the bug is that the iterator calls `setDescription()` for any value type without type checking

- Correct approach example:
  ```java
  @Test
  void testDescriptionNotOverwrittenByNonString() {
    MicroserviceFactory factory = new MicroserviceFactory();
    Map<String, Object> map = new HashMap<>();
    map.put("description", new CtTypeReference()); // non-String type
    // ... other required fields ...

    Microservice ms = factory.createMicroservice(map);
    assertNull(ms.getDescription());
  }
  ```

- Incorrect approach example:
  ```java
  @Test
  void testDescriptionMapEntry() {
    MicroserviceFactory factory = new MicroserviceFactory();
    Map<String, Object> map = new HashMap<>();
    map.put("description", "valid description");

    Microservice ms = factory.createMicroservice(map);
    assertEquals("valid description", ms.getDescription()); // only tests String path
  }
  ```