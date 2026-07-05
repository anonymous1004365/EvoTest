---
name: creator-collector-property-handling
description: When validating and collecting creator properties with settable bean
  properties, test that both String-typed and CtTypeReference-typed parameters are
  correctly handled, and that properties with matching names but different types are
  not inadvertently overwritten. Use this skill when the code maps property names
  to settable bean properties using type-sensitive checks.
code_tags:
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# creator-collector-property-handling

## Instructions

# CreatorCollector Property Handling

## Instructions

WHEN the TG encounters code that collects or validates creator properties (constructor/factory parameters) and maps them to settable bean properties (e.g., `SettableBeanProperty`), AND the code uses property name matching combined with type checking (e.g., checking if a property's type is a `String`, `CtTypeReference`, or other type before deciding how to process it):

- THEN the TG should write a parametrized test that provides both a `String`-typed property and a custom object-typed property (e.g., `CtTypeReference`) that share the **same property name**, and verify that:
  1. Both properties are correctly collected without one overwriting the other
  2. The mapping from property names to `SettableBeanProperty` instances maintains both entries correctly
  3. No `NullPointerException`, `ClassCastException`, or silent data loss occurs during the collection process

- THEN the TG should test at least these type pairs:
  - A `String` value for one property and a domain object (e.g., `CtTypeReference`, `AnnotatedElement`, `Class<?>`) for the other
  - Both properties using the SAME name (e.g., `"template"` or `"targetType"`)
  - Properties registered in different orders to verify order independence

- THEN the test should exercise the method that processes creator parameter candidates (e.g., methods like `addProperty`, `_handleCreatorProperty`, or parameter collection loops) and assert that:
  - No exception is thrown during property collection
  - All properties exist in the resulting mapping
  - Properties retain their correct types (no type erasure or replacement)

- Common pitfalls to avoid:
  - ❌ Testing only with `String`-typed parameters, which misses the bug when non-String typed properties share the same name
  - ❌ Assuming property names are unique keys and overwriting is safe, when type information must be preserved
  - ❌ Not testing the ordering of property registration (A then B vs B then A)
  - ❌ Testing only the happy path where all properties have distinct names and the same type

**Incorrect test pattern (too narrow):**
```java
@Test
void testSinglePropertyCollection() {
    CreatorCollector collector = new CreatorCollector(...);
    collector.addProperty(new SettableBeanProperty("name", String.class, ...));
    assertThat(collector.properties()).containsKey("name");
}
```
This test would pass on the buggy code but does NOT trigger the bug because it only tests `String`-typed properties with distinct names.

**Correct test pattern (triggers the bug):**
```java
@ParameterizedTest
@ValueSource(strings = {"template", "targetType", "filter"})
void testMixedTypePropertiesWithSameName(String propertyName) {
    // Given two properties with the SAME name but DIFFERENT types
    SettableBeanProperty stringProp = createStringProperty(propertyName);
    SettableBeanProperty objectProp = createCtTypeReferenceProperty(propertyName);
    
    CreatorCollector collector = new CreatorCollector(...);
    
    // When both are added - order matters, test both permutations
    collector.addProperty(stringProp);
    collector.addProperty(objectProp);
    
    // Then both should be retained without one overwriting the other
    Map<String, SettableBeanProperty> props = collector.properties();
    assertThat(props.get(propertyName)).isNotNull();
    // The fix should handle both types without losing data
}

private SettableBeanProperty createStringProperty(String name) {
    return new SettableBeanProperty(name, String.class, ...);
}

private SettableBeanProperty createCtTypeReferenceProperty(String name) {
    return new SettableBeanProperty(name, CtTypeReference.class, ...);
}
```