---
name: creator-verify-nondup-return-value-handling
description: When a method like verifyNonDup is changed from void to boolean to indicate
  whether a creator should be used, callers must guard state mutations behind the
  boolean check. This skill teaches when and how to test that state is not overwritten
  when verifyNonDup returns false.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# creator-verify-nondup-return-value-handling

## Instructions

# Creator Deduplication Return Value Handling

## Instructions

- WHEN the TG encounters code where a method (e.g., `verifyNonDup`) was changed from `void` to `boolean` return, and its callers previously unconditionally mutated state (e.g., `_propertyBasedArgs = properties`, `_delegateArgs = injectables`)
- THEN the TG should test that when multiple candidate creators exist (e.g., one explicit `@JsonCreator` constructor and another constructor without annotation), the non-chosen creator does NOT overwrite the state fields of the chosen creator. Specifically:
  - Create a POJO with two constructors annotated with `@JsonCreator` (or one explicit + one implicit), where the first-registered constructor has a superset of properties compared to the second
  - Deserialize JSON that uses the properties of the first constructor
  - Verify deserialization succeeds and returns the correct values **without** throwing `JsonMappingException` mentioning "Could not find creator property with name ..."
  - The key insight: if `_propertyBasedArgs` is overwritten by a rejected creator (because the boolean return of `verifyNonDup` was ignored), then property names from the first creator will be lost, causing a "Could not find creator property" error

- WHEN testing `CreatorCollector.addPropertyCreator`, verify that when `verifyNonDup` returns `false` (i.e., a more specific or already-existing creator is retained), `_propertyBasedArgs` is NOT overwritten with the new properties. The fix wraps the entire `_propertyBasedArgs = properties` assignment inside `if (verifyNonDup(...)) { ... }`.

- Common pitfalls to avoid:
  - **Testing only with a single creator**: The bug only manifests when multiple creators compete for the same typeIndex. Test with at least two constructors/factory methods.
  - **Not checking the error message**: The bug produces a `JsonMappingException` with message "Could not find creator property with name 'X'". Assert that no such exception occurs.
  - **Overlooking that verifyNonDup can return false via multiple paths**: When the old creator is more specific (`newType.isAssignableFrom(oldType)`), when the old creator is explicit and new is not, or when a `@JsonCreator` with `mode=DELEGATING` loses to a properties-based creator. Test at least the "old is more specific" case.

- Correct approach:
  ```java
  // POJO with two constructors — first is more specific
  static class MyPojo {
      int intField;
      String stringField;
      
      @JsonCreator
      public MyPojo(@JsonProperty("intField") int intField, 
                    @JsonProperty("stringField") String stringField) {
          this.intField = intField;
          this.stringField = stringField;
      }
      
      // This constructor is a fallback but must not overwrite _propertyBasedArgs
      // when verifyNonDup rejects it
      public MyPojo(@JsonProperty("stringField") String stringField) {
          this.stringField = stringField;
      }
  }
  
  @Test
  public void testConstructorSelectionPreservesProperties() throws Exception {
      ObjectMapper mapper = new ObjectMapper();
      MyPojo result = mapper.readValue(
          "{\"intField\": 1, \"stringField\": \"foo\"}", 
          MyPojo.class);
      assertEquals(1, result.intField);
      assertEquals("foo", result.stringField);
  }
  ```

- Incorrect approach (what the TG might write without this skill):
  ```java
  // Only tests with a single constructor — misses the bug entirely
  @Test
  public void testSingleConstructor() throws Exception {
      ObjectMapper mapper = new ObjectMapper();
      // This passes on BOTH buggy and fixed versions, so it's useless
      SimplePojo result = mapper.readValue(
          "{\"intField\": 1}", SimplePojo.class);
      assertEquals(1, result.intField);
  }
  ```