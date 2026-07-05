---
name: metamodel-getter-setter-role-consistency
description: When defining mapping roles between model elements (like getters/setters
  for metamodel attributes), ensure the role-object pair is registered for both directions
  and that property descriptors are properly initialized before role retrieval. Use
  this skill when validating bidirectional metamodel role mappings.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# metamodel-getter-setter-role-consistency

## Instructions

# Metamodel Getter/Setter Role Consistency

## Instructions

WHEN a class defines roles for getter and setter methods of a metamodel attribute (e.g., a `CtRole` for a getter and a separate `CtRole` for the corresponding setter), and the roles are registered as mapping entries between a `CtRole` and the corresponding `PropertyDescriptor`:

- THEN the test MUST verify that for each `PropertyDescriptor` that has both a getter role and a setter role, calling `getRole("getter")` and `getRole("setter")` on the descriptor returns the correct role objects — i.e., `getRole("getter")` should NOT return the setter's role, and vice versa.
- THEN the test MUST verify the consistency of the mapping by iterating over the `PropertyDescriptor` collection and checking that for every property, the getter role (when present) maps back to the correct descriptor, and the setter role (when present) also maps back to the correct descriptor.
- THEN the test MUST check that the role-object mappings are bidirectional: if a `CtRole` is mapped to a descriptor, then looking up that descriptor's getter/setter keys should resolve back to the same `CtRole`.
- Common pitfalls:
  - ❌ Testing only one direction (e.g., only checking that a role maps to a descriptor, without verifying the descriptor's role lookup returns the same role).
  - ❌ Confusing getter roles with setter roles — the test MUST check BOTH "getter" and "setter" strings as keys in the role lookup.
  - ❌ Assuming that because a property exists, its roles are automatically registered. The fix may involve adding missing role entries to the mapping.

### Correct Example (catching the bug)
```java
// Iterate over all PropertyDescriptors and verify bidirectional mapping
for (PropertyDescriptor<?> property : propertyDescriptors) {
    Object role = mapping.get(property);  // mapping: Map<Object, PropertyDescriptor<?>>
    if (role != null) {
        // Verify that the role's getter/setter lookup resolves back to this property
        CtRole getterRole = property.getRole("getter");
        CtRole setterRole = property.getRole("setter");
        // On the buggy version, getter/setter roles may be swapped or missing
        assertThat(getterRole).as("getter role for " + property).isNotNull();
        assertThat(setterRole).as("setter role for " + property).isNotNull();
        // Verify the role maps back to the correct property
        assertThat(mapping.get(getterRole)).isEqualTo(property);
        assertThat(mapping.get(setterRole)).isEqualTo(property);
    }
}
```

### Incorrect Example (missing the bug)
```java
// Only checks that roles exist, not that they map correctly
for (PropertyDescriptor<?> property : propertyDescriptors) {
    assertThat(mapping.get(property)).isNotNull();
    // BUG: Does not verify that the property's getter/setter roles
    // actually round-trip back to the same property descriptor.
    // On the buggy version, this test would pass even though
    // the getter/setter role mapping is incorrect.
}
```