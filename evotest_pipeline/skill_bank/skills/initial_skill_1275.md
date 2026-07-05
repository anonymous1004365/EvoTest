---
name: creator-collector-state-initialization
description: When constructing deserializer creators with @JsonCreator, test that
  the CreatorCollector correctly initializes its internal state by verifying that
  explicit creator annotations on constructors/methods are properly detected and not
  missed due to delegation precedence issues.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# creator-collector-state-initialization

## Instructions

# CreatorCollector State Initialization on @JsonCreator

## Instructions

- WHEN the TG encounters code that collects creator candidates (constructors/factory methods annotated with `@JsonCreator`) and stores them in a `CreatorCollector` object
  - THEN the TG should write a test that verifies the **internal state** (`_creators` array, `_hasNonDefaultCreator` flag, `_explicitCreators` flag) is correctly populated after processing constructors/methods with explicit `@JsonCreator(mode=JsonCreator.Mode.PROPERTIES)` or `@JsonCreator(mode=JsonCreator.Mode.DELEGATING)`
  - Specifically, test that when at least one explicit `@JsonCreator(mode=PROPERTIES)` is present, the delegate creator (`_delegateCreator`) is NOT incorrectly set, and the explicit property-based creator IS used
  - Verify that `_hasNonDefaultCreator` is set to `true` and `_explicitCreators` properly reflects whether any creator was explicitly declared (vs. implicitly discovered)
  - Include concrete examples: a POJO with `@JsonCreator` on both a constructor and a factory method, testing that the correct one is selected based on mode

- WHEN the TG encounters a test that validates creator selection logic (e.g., which creator a `BeanDeserializerFactory` selects when multiple candidates exist)
  - THEN the TG should ensure the test checks that a constructor-only `@JsonCreator(mode=PROPERTIES)` does NOT trigger the delegation path, meaning the resulting deserializer still uses property-based binding
  - Common pitfalls: Testing only with `@JsonCreator` without specifying mode (implicit mode may behave differently); assuming that any `@JsonCreator` automatically means delegation; forgetting to verify that a constructor marked `@JsonCreator` actually participates in property-based deserialization correctly (i.e., its parameters are bound by name)

- WHEN the TG validates creator selection after adding creators to the collector
  - THEN the test must inspect the final `JsonDeserializer` produced by the deserialization pipeline (e.g., via `ObjectMapper`), not just the internal `CreatorCollector` state directly
  - Verify by serializing and deserializing a test object, and confirming that properties are correctly bound through the selected creator

## Correct Example

```java
// Correct: Tests that a constructor with @JsonCreator(mode=PROPERTIES) produces
// a property-based deserializer (not a delegate deserializer)
@Test
void testExplicitPropertyBasedCreatorIsSelected() throws Exception {
    ObjectMapper mapper = new ObjectMapper();
    // POJO with explicit @JsonCreator(mode=PROPERTIES) constructor
    String json = mapper.writeValueAsString(new MyClass("foo", 42));
    MyClass result = mapper.readValue(json, MyClass.class);
    assertEquals("foo", result.name);
    assertEquals(42, result.value);
}
```

## Incorrect Example

```java
// Incorrect: Only tests that no exception is thrown, doesn't verify
// the actual deserialization behavior or creator selection
@Test
void testCreatorDoesNotThrow() {
    ObjectMapper mapper = new ObjectMapper();
    // This passes even if delegate creator is incorrectly used
    assertDoesNotThrow(() -> mapper.readValue("{\"name\":\"foo\"}", MyClass.class));
}
```

## Common Pitfalls

- Testing only that the code doesn't crash, without verifying actual deserialization semantics (property binding vs delegation)
- Relying on implicit `@JsonCreator` mode, which may default to `DELEGATING` in certain configurations, masking the bug
- Not testing the round-trip (serialize → deserialize → assert) to confirm that all properties are correctly resolved through the chosen creator