---
name: delegate-creator-conflict-detection
description: When detecting that multiple delegate creators may conflict in a Jackson
  deserializer, the test should verify that a more specific delegate creator is correctly
  preferred over a less specific one (e.g., a Collection-like type delegate vs a general
  Object delegate) and that JsonMappingException is NOT thrown when the correct creator
  can be determined.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# delegate-creator-conflict-detection

## Instructions

# Delegate Creator Conflict Detection

## Instructions

- WHEN the TG encounters a `CreatorCollector` class (or similar Jackson deserialization creator resolution logic) that collects multiple `@JsonCreator` annotated constructors/factory methods, including one delegate creator that accepts a `Collection`-like type (e.g., `List`, `Set`) and another that accepts a more general type (e.g., `Object`, `String`)
- THEN the TG should write a test that:
  1. Defines a POJO class with at least TWO `@JsonCreator` constructors or factory methods — one accepting a `Collection`-like type (e.g., `List<String>`) and another accepting a more general type (e.g., `Object` or `String`)
  2. Attempts to deserialize JSON that should match the MORE SPECIFIC (Collection-like) creator, e.g., `{"intField": 1, "stringField": "foo"}`
  3. Verifies that deserialization SUCCEEDS (no exception thrown) and the correct specific creator is used
  4. **Be aware**: The bug causes `addPropertyCreator` to overwrite `_propertyBasedArgs` even when `verifyNonDup` determines the new creator should NOT replace an existing explicit creator. On the buggy version, this can cause `JsonMappingException` with message like "Could not find creator property with name 'intField'" because the wrong creator was stored.

- **Common pitfalls to avoid**:
  - ❌ Testing only a single creator — the bug only manifests when MULTIPLE creators compete
  - ❌ Not marking creators explicitly with `@JsonCreator` — the fix involves `explicit` flag handling
  - ❌ Assuming that if one creator is more generic, it will always be correctly replaced by a more specific one — the bug causes the assignment to happen regardless of whether replacement was accepted
  - ❌ Testing only with one type parameter (e.g., only `String`) — the bug specifically involves the type comparison logic between `Collection`-like and non-Collection types

- **Correct test example** (Java):
  ```java
  static class SimplePojo {
      public int intField;
      public String stringField;
      
      @JsonCreator
      public SimplePojo(Object obj) {
          // generic constructor
      }
      
      @JsonCreator
      public SimplePojo(Map<String, Object> map) {
          this.intField = ((Number) map.get("intField")).intValue();
          this.stringField = (String) map.get("stringField");
      }
  }
  
  // Positive test - should succeed
  @Test
  public void testConstructorChoice() {
      SimplePojo result = new ObjectMapper().readValue(
          "{ \"intField\": 1, \"stringField\": \"foo\" }", 
          SimplePojo.class
      );
      assertEquals(1, result.intField);
      assertEquals("foo", result.stringField);
  }
  ```

- **Incorrect test examples** (would NOT catch the bug):
  ```java
  // ❌ Tests with only one constructor - won't trigger the conflict logic
  static class SingleCreator {
      @JsonCreator
      public SingleCreator(Map<String, Object> map) { }
  }
  
  // ❌ Tests with property-based constructor only - no delegate conflict
  static class PropsOnly {
      @JsonCreator
      public PropsOnly(@JsonProperty("x") int x) { }
  }
  ```