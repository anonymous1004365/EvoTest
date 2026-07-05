---
name: defensive-copy-for-address-objects
description: When a class has a copy constructor or clone method that assigns immutable-typed
  fields (like String) but shares mutable-typed fields (like maps between String and
  List), the copy must defensively copy the mutable fields to prevent unintended mutation
  of the original object's state.
code_tags:
- SAFE_COPY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# defensive-copy-for-address-objects

## Instructions

# Defensive Copy for Composite Address-Like Objects

## Instructions

- WHEN the TG encounters a class that provides a copy constructor (e.g., `Address(Address other)`) or copy method that copies fields from a source object to a new one, AND some fields are simple immutable types (like `String`, `int`) but others are mutable reference types (like `Map<String, List<String>>` or `Map<String, List<X>>`)
- THEN the TG should verify that mutable fields are defensively copied (e.g., by creating a new `HashMap` or `ArrayList`) and NOT just assigned by reference (`this.field = other.field`). The TG should write a test that:
  1. Creates an original object.
  2. Creates a copy of that object via the copy constructor/copy method.
  3. Modifies the **copied** object's mutable field (e.g., adds/removes entries in a map).
  4. Asserts that the **original** object's mutable field is NOT affected by the modification.
  5. If the copy shares references instead of making deep copies, the test will fail on the buggy version.

- Common Pitfalls:
  - Testing only immutable/String fields: these are naturally safe to share via reference assignment because they are immutable. The bug is in the mutable reference fields.
  - Testing the copy constructor's null-handling without testing its state-independence. The skill is about state isolation, not null safety.
  - Assuming that because all fields appear to be "copied" (assigned), the copy is independent. The TG must specifically identify which fields are mutable containers and verify they are new instances.

### Example (Correct Test)

```java
@Test
public void testCopyIsDefensiveForMutableFields() {
    Address original = new Address();
    original.setAnnotations(Map.of("key", List.of("value1")));
    
    Address copy = new Address(original);
    
    // Modify the copy's mutable field
    copy.getAnnotations().put("newKey", List.of("newValue"));
    
    // Original must NOT be affected
    assertEquals(1, original.getAnnotations().size());
    assertFalse(original.getAnnotations().containsKey("newKey"));
}
```

### Example (Incorrect — Will NOT catch the bug)

```java
@Test
public void testCopyBasicFields() {
    Address original = new Address("foo", "bar");
    Address copy = new Address(original);
    assertEquals(original.getName(), copy.getName());
    // This passes on both buggy and fixed versions — doesn't test mutable field isolation
}
```