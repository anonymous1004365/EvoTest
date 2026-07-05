---
name: property-removal-via-null-setproperty
description: When testing JCR Node.setProperty() with null value to remove a property,
  the test should verify that setting a property to null (type-cast) removes the property
  instead of throwing an exception, especially for non-existent properties.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# property-removal-via-null-setproperty

## Instructions

# Property Removal via Null setProperty

## Instructions

- WHEN the TG encounters a method that calls `setProperty(String name, null)` or `setProperty(String name, null, int type)` on a JCR `Node` to remove a property
  - THEN the TG should write a test that:
    1. Creates a `Node` (e.g., via `session.getRootNode().addNode("testNode")` or using the root node directly)
    2. Calls `node.setProperty("anyPropertyName", (String) null)` — casting null to String is essential
    3. Verifies no exception is thrown (the call should succeed)
    4. Verifies the property is truly gone: `assertFalse(node.hasProperty("anyPropertyName"))`
  - Include an additional test where the property never existed at all (i.e., set a property to null on a node that never had that property) — this should also succeed without exception
  - Expect that on the buggy version, calling `node.setProperty("nonExistentProp", (String) null)` throws a `RepositoryException` with message like `"... not found on ..."`. The test should use `Assert.assertThrows(RepositoryException.class, () -> node.setProperty("missing", (String) null))` to verify the bug, then confirm the fixed version passes without exception.

- Common pitfalls to avoid:
  - **Using an untyped `null`**: `node.setProperty("name", null)` alone may call `setProperty(String, Value)` which behaves differently; always cast null: `(String) null` or `(Calendar) null` or pass the appropriate type signature.
  - **Only testing with existing properties**: The bug manifests specifically when removing a property that never existed. Test both cases — removing an existing property and removing a non-existent property.
  - **Forgetting to save/logout**: Ensure the session is saved and the test uses `session.logout()` in a `finally` block or try-with-resources to clean up.
  - **Not checking `hasProperty`**: A successful null-setProperty should result in `hasProperty` returning `false` for that property name.

### Correct Example (Fixed Version Passes)

```java
// Test that setting property to null removes it (even if property never existed)
Node root = session.getRootNode();
root.setProperty("missing", (String) null);
assertFalse(root.hasProperty("missing"));
```

### Incorrect Example (Does Not Catch The Bug)

```java
// WRONG: Does not test with a non-existent property, only tests with an existing property
Node root = session.getRootNode();
root.setProperty("existingProp", "value");
root.setProperty("existingProp", (String) null);
assertFalse(root.hasProperty("existingProp"));
// This passes even on the buggy version because existingProp existed before removal
```

### Buggy Version Behavior

```java
// On the buggy version, this throws RepositoryException: "missing not found on /"
Node root = session.getRootNode();
assertThrows(RepositoryException.class, () -> {
    root.setProperty("missing", (String) null);
});
```