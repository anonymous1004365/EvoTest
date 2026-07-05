---
name: template-parameter-prefix-validation
description: When creating property states with NAME type values, the TG should verify
  that namespace/prefix information is correctly preserved and not replaced by default
  values. This skill applies when converting between different name representations
  (String vs Name vs OakValue).
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# template-parameter-prefix-validation

## Instructions

# Template Parameter Prefix Validation

## Instructions

- WHEN the TG encounters code that creates `PropertyState` instances with `PropertyType.NAME` values (e.g., via `PropertyStates.createProperty("name", value, PropertyType.NAME)`) — particularly when the value is a `String` containing a prefixed JCR name like `"oak-prefix:value"`
- THEN the TG should write a test that:
  1. Creates a `PropertyState` by calling the factory method with a `String` value containing a custom namespace prefix (e.g., `"oak-prefix:value"` or `"my-ns:localName"`)
  2. Calls `propertyState.getValue(Type.STRING)` and asserts that the returned string **still contains the original prefix** — not a different default prefix such as `"jcr-prefix:value"`
  3. Verifies that the `getName()` method returns the correct property name that was passed in
  4. For the buggy version, the test should fail with an assertion error like `expected:<...oak-prefix...> but was:<...jcr-prefix...>`

- The TG should use the triggering test pattern: create a value with a specific prefix in the name portion of the value string, then assert the exact string output after storing and retrieving the value.

- **Common pitfalls to avoid**:
  - ❌ Testing only with un-prefixed values (e.g., just `"value"`) — this will NOT detect the prefix replacement bug
  - ❌ Testing only with a single prefix that happens to match the default — the bug manifests specifically when a custom/non-default prefix is used
  - ❌ Only testing with `Name` type parameters instead of `String` type parameters — the bug occurs in the `String`-to-`OakValue` conversion path
  - ❌ Only verifying the property name but not the stored value's string representation

### Correct test approach

```java
@Test
public void testNamePropertyPreservesCustomPrefix() {
    // Create a property state with a NAME value that has a custom namespace prefix
    PropertyState ps = PropertyStates.createProperty(
        "propName", 
        "oak-prefix:value", 
        PropertyType.NAME
    );
    
    // The string value must preserve the original prefix
    assertEquals("propName", ps.getName());
    assertEquals("oak-prefix:value", ps.getValue(Type.STRING));
}
```

### Incorrect test approach (would miss the bug)

```java
@Test
public void testNameProperty() {
    // Only tests without a prefix — will NOT catch the prefix replacement bug
    PropertyState ps = PropertyStates.createProperty(
        "propName", 
        "value", 
        PropertyType.NAME
    );
    
    assertEquals("propName", ps.getName());
    assertEquals("value", ps.getValue(Type.STRING));
    // This passes even on the buggy version
}
```