---
{}
---

---
name: empty-multi-valued-property-undefined-type
description: When creating multi-valued properties from an empty value list, the PropertyStates.createProperty method incorrectly defaults to STRINGS type. A proper test should verify that empty multi-valued properties with different type assumptions (e.g., UNDEFINEDS) don't trigger 'Invalid type: UNDEFINEDS' errors in the EffectiveType.getDefinition method.
code_tags: ['VALIDATION', 'TYPE_CONVERSION', 'BOUNDARY_CHECK']
test_pattern: PARAMETRIC_TEST
---

# empty-multi-valued-property-undefined-type

## Instructions

# Empty Multi-Valued Property Type Validation

## Instructions

- WHEN the TG encounters code that creates a multi-valued `PropertyState` from an empty `Iterable<Value>`, specifically the `createProperty(String name, Iterable<Value> values)` method in `PropertyStates.java`
- THEN it should test that:
  1. Calling `createProperty("propName", Collections.<Value>emptyList())` does NOT throw `IllegalArgumentException("Invalid type: UNDEFINEDS")` or any other exception related to undefined types
  2. The resulting `PropertyState` has a valid `Type` — specifically, it should return `Type.STRINGS` (since the current fallback is `EmptyPropertyState.emptyProperty(name, STRINGS)`) without causing errors when its type tag is checked downstream
  3. Any downstream code that iterates the property's type tag (like `EffectiveType.getDefinition(PropertyState)` which calls `propertyType.toString()` and compares against `UNDEFINEDS.toString()`) must be tested to ensure the string "UNDEFINEDS" does NOT appear in the property type's string representation
- WHEN writing this test, include concrete types and values:
  - Use `org.apache.jackrabbit.oak.api.Type.UNDEFINEDS` to check that the fallback type is NOT `UNDEFINEDS`
  - Use `org.apache.jackrabbit.oak.api.Type.STRINGS` to verify the current default for empty multi-valued properties
  - The failure message `"Invalid type: UNDEFINEDS"` originates from `PropertyStates.java` line 249 in the `createProperty(String name, Iterable<Value> values)` default branch, via `Type.fromTag(type, true)` where `type` is `PropertyType.UNDEFINED`
- Common pitfalls to avoid:
  - Testing ONLY with non-empty value lists — the bug is specific to the EMPTY values case
  - Forgetting that the `Type.fromTag(PropertyType.UNDEFINED, true)` call maps to `Type.UNDEFINEDS` which has string representation `"UNDEFINEDS"`, causing the downstream `EffectiveType.getDefinition()` to fail
  - Assuming any empty multi-valued property will work — the fix should ensure empty multi-valued properties default to a well-known type like `STRINGS` rather than trying to derive from undefined values
- Examples:

**Correct test approach** (verifying the fix works):
```java
@Test(expected = IllegalArgumentException.class)
public void createEmptyMultiValueUndefinedType() throws RepositoryException {
    // This should NOT throw if the fix is in place
    // If the fix defaults to STRINGS, this should succeed
    ValueFactory vf = session.getValueFactory();
    PropertyState ps = PropertyStates.createProperty("testProp", 
        Collections.<Value>emptyList());
    // The type should be STRINGS, not UNDEFINEDS
    assertEquals(Type.STRINGS, ps.getType());
}

@Test(expected = IllegalArgumentException.class)
public void createEmptyMultiValueUndefinedTypeThrows() throws RepositoryException {
    // Simulating the buggy behavior by directly creating with UNDEFINED type
    PropertyState ps = PropertyStates.createProperty("testProp", 
        Collections.<Value>emptyList());
    // In buggy version, if type was UNDEFINEDS, this would throw
    // Invalid type: UNDEFINEDS when calling Type.fromTag(PropertyType.UNDEFINED, true)
    EffectiveType effective = ...;
    NodeState def = effective.getDefinition(ps);
    // Should not throw IllegalArgumentException("Invalid type: UNDEFINEDS")
}
```

**Incorrect test approach** (does not catch the bug):
```java
@Test
public void createEmptyMultiValue() throws RepositoryException {
    // Only testing with non-empty values — never exercises the empty path
    ValueFactory vf = session.getValueFactory();
    PropertyState ps = PropertyStates.createProperty("testProp", 
        Arrays.asList(vf.createValue("test")));
    // This passes even with the bug present
    assertNotNull(ps);
}
```