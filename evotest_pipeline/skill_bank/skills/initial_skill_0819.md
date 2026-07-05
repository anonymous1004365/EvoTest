---
name: field-query-map-synthetic-field-exclusion
description: When encoding query map parameters from object fields via reflection,
  synthetic fields (e.g., 'this$0' for inner class references) must be excluded to
  prevent leaking internal object state into query parameters. Use this skill when
  testing reflection-based encoders that iterate over declared fields.
code_tags:
- FIELD_QUERY_MAP_ENCODING
- OBJECT_STATE_REFLECTION
test_pattern: STATE_TEST
---

# field-query-map-synthetic-field-exclusion

## Instructions

# Reflection Field Encoding Should Exclude Synthetic Fields

## Instructions

- WHEN the TG encounters code that reflects over an object's fields (e.g., `Class.getDeclaredFields()`, `FieldQueryMapEncoder`) and uses them to build query parameters or serialized output
- THEN the TG should test with an object that declares both data fields AND has an enclosing (non-static) inner class relationship, verifying that the encoder does NOT include the synthetic `this$0` field (or any field where `Field.isSynthetic()` returns true) in its encoded output
  - Specifically: create a non-static inner class (or anonymous class) inside the test class that contains regular fields like `String foo`, `String bar`
  - Instantiate that inner class from the test method and pass it to the encoder
  - Verify the encoded map contains ONLY the explicitly declared fields (`foo`, `bar`) and NOT the synthetic `this$0` reference
  - The expected behavior is that `field.isSynthetic()` fields are filtered out before encoding
  - Also test that a normal POJO (top-level class, not an inner class) works correctly with the encoder

- Common pitfalls:
  - Testing only top-level classes and missing the inner class case entirely
  - Using a static inner class (which does NOT have a `this$0` synthetic field) instead of a non-static inner class
  - Asserting the map is empty when fields exist but are null (null/default fields should still appear as keys)
  - Forgetting that primitive `int` fields default to `0` and should still produce a map entry

- Example (correct):
  ```java
  // Test: inner class object should not leak synthetic fields
  class InnerPojo {
    String foo = "fooz";
    String bar = "barz";
  }
  
  FieldQueryMapEncoder encoder = new FieldQueryMapEncoder();
  Map<String, Object> encoded = encoder.encode(new InnerPojo());
  
  // this$0 field should not appear in the map
  assertThat(encoded).containsOnlyKeys("foo", "bar");
  assertThat(encoded).containsEntry("foo", "fooz");
  assertThat(encoded).containsEntry("bar", "barz");
  ```

- Example (incorrect — buggy behavior would pass this):
  ```java
  // WRONG: Only checks top-level class, won't catch synthetic field leakage
  class Pojo {
    String foo = "fooz";
  }
  
  Map<String, Object> encoded = encoder.encode(new Pojo());
  // This passes even in buggy code — no inner class, no synthetic field!
  ```

- Example (pitfall — static inner class won't trigger the bug):
  ```java
  // WRONG: Static inner classes don't have synthetic this$0 fields
  static class StaticPojo {
    String foo = "fooz";
  }
  // This test passes even on buggy code, giving false confidence
  ```