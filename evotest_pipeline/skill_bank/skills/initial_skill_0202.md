---
name: proxy-batchwriter-mutation-type-validation
description: When ProxyServer receives an update mutation via Thrift, the ColumnUpdate's
  value and colFamily/colQualifier may contain heterogeneous types. The TG should
  test that both String-based and fully-qualified CtTypeReference-based mutations
  are correctly serialized to KeyValue.
code_tags:
- STATE_MUTATION
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# proxy-batchwriter-mutation-type-validation

## Instructions

# ProxyServer Mutation Type Handling

## Instructions

- WHEN the TG encounters a `ProxyServer` method that converts Thrift `ColumnUpdate` objects (with `colFamily`, `colQualifier`, `colVisibility`, `value` fields) into Accumulo `KeyValue` pairs for a `BatchWriter`
- THEN it should write a **parametric test** that feeds the conversion logic with:
  - **String-based mutations** (e.g., `ColumnUpdate` with plain Java `String` values like `"cf"`, `"cq"`, `"val"`)
  - **CtTypeReference-based mutations** (e.g., `ColumnUpdate` whose fields are set via `CtTypeReference` objects from Spoon or similar bytecode representation)
- The test must verify that **both** input types produce identical `KeyValue` bytes, and that **neither** triggers a `ClassCastException`, `NullPointerException`, or silent corruption during the conversion to Accumulo mutations
- **Common pitfalls to avoid:**
  - Testing only with `String`-type parameters (the bug was that `CtTypeReference`-typed values triggered a failure while `String` values passed successfully — both must be tested)
  - Testing the `BatchWriter` directly without isolating the mutation conversion step (test the conversion logic in isolation to avoid depending on the full Proxy stack)
  - Assuming the `ColumnUpdate` fields are always `String` — they are declared as `ByteBuffer` in Thrift and can carry typed objects
- **Correct approach example:**
  ```java
  // Parametric test with both types
  @ParameterizedTest
  @ValueSource(classes = {String.class, CtTypeReference.class})
  void testMutationConversionWithDifferentTypes(Class<?> valueType) {
      ColumnUpdate update = createColumnUpdate(valueType); 
      // ... convert to KeyValue and verify output
  }
  ```
- **Incorrect approach example:**
  ```java
  // Only testing with String — misses the bug!
  @Test
  void testMutationConversion() {
      ColumnUpdate update = createStringColumnUpdate();
      // ... only String case covered
  }
  ```