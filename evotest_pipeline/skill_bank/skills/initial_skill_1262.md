---
name: delegate-creator-property-type-validation
description: When deserializers delegate to creator methods with settable properties,
  the TG should test that all property types (e.g., String, int, long, double, boolean,
  arrays, enums, CtTypeReference) are correctly resolved and assigned in both CreatorProperty
  and SettableBeanProperty contexts.
code_tags:
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# delegate-creator-property-type-validation

## Instructions

# Delegate Creator Property Type Validation

## Instructions

- WHEN the TG encounters a `CreatorCollector` or `SettableBeanProperty`-based delegate creator that handles multiple property types via a `CreatorProperty` list  
  THEN it MUST write a parametric test that exercises each property type with concrete values and verifies that the deserialized object's fields match.

- WHEN a delegate creator method has a signature like `(String, int, long, double, boolean, int[], String[], SomeEnum, CtTypeReference)`  
  THEN the test MUST construct a JSON payload containing values for all parameter types (including arrays and enums), call `MAPPER.readValue(json, Cls.class)`, and assert that each property equals the expected value.

- WHEN verifying the fix for type resolution in `CreatorCollector`'s delegation path  
  THEN the test MUST specifically verify that a property backed by a `CtTypeReference` type parameter is not resolved to `Object.class` but to its actual type, and that deserialization completes without a `JsonMappingException` about type mismatch.

- Common pitfalls to avoid:
  - Testing only with a single `String` property — this misses type resolution bugs in non-trivial parameter types like `CtTypeReference`.
  - Relying only on `@JsonCreator` with static factory methods — this bug is specific to **delegate** creators where the creator method takes `SettableBeanProperty[]` and iterates over `CreatorProperty` objects.
  - Assuming that if one property type works, all do — the bug was triggered because a `CtTypeReference` property failed to resolve its type during `CreatorProperty` construction.

- Correct example (what to do):
  ```java
  @Test
  public void testDelegateCreatorWithMixedTypes() throws Exception {
      String json = "{\"name\":\"test\",\"count\":42,\"ratio\":3.14,\"active\":true,\"codes\":[1,2],\"tags\":[\"a\",\"b\"]}";
      ResultType result = MAPPER.readValue(json, ResultType.class);
      assertEquals("test", result.name);
      assertEquals(42, result.count);
      assertEquals(3.14, result.ratio, 0.001);
      assertTrue(result.active);
      assertArrayEquals(new int[]{1, 2}, result.codes);
      assertArrayEquals(new String[]{"a", "b"}, result.tags);
  }
  ```

- Incorrect example (what to avoid):
  ```java
  @Test
  public void testDelegateCreatorStringOnly() throws Exception {
      // BUG: Only tests String, misses type resolution failure for CtTypeReference
      String json = "{\"name\":\"test\"}";
      ResultType result = MAPPER.readValue(json, ResultType.class);
      assertEquals("test", result.name);
  }
  ```