---
name: general-collection-mutation-copy
description: When a method mutates an internal collection or adds elements to a collection
  returned from a getter, write tests that verify the returned collection is a defensive
  copy and that mutations to it do NOT affect internal state.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# general-collection-mutation-copy

## Instructions

# General Collection Mutation / Defensive Copy Test

## Instructions

- WHEN the TG encounters a method that returns a collection (List, Set, Map, etc.) from inside an object, or a method that adds/modifies elements in an internal collection — THEN the TG should write a test that:
  1. Gets the collection from the object
  2. Mutates the returned collection (e.g., add, remove, clear)
  3. Re-gets or checks the internal state of the object to verify the mutation did NOT corrupt the object's internal state

- Include concrete examples of the mutation operations used (e.g., `add()`, `remove()`, `clear()`) and verify that the internal collection is protected (either via unmodifiable wrapper or defensive copy).

- WHEN the TG encounters an object that takes a collection in a setter AND exposes it via a getter — THEN the TG should write a test that:
  1. Creates a mutable collection
  2. Passes it to the setter
  3. Mutates the original collection reference after setting
  4. Verifies the object is NOT affected by the external mutation

- Common mistakes to avoid:
  - Testing only that a getter returns *something* without checking immutability/defensive copying
  - Writing the test in a way that would pass on BOTH buggy and fixed versions (the test should FAIL on the buggy version where defensive copying is missing)
  - Testing only getter mutation without testing setter-side aliasing

- Example of a **correct** test:
```java
@Test(expected = UnsupportedOperationException.class)
public void testListIsUnmodifiable() {
    SomeClass obj = new SomeClass();
    obj.addItem("foo");
    List<String> items = obj.getItems();
    items.add("bar"); // Should throw UnsupportedOperationException
}

// OR, if defensive copy is used instead of unmodifiable:
@Test
public void testListIsDefensiveCopy() {
    SomeClass obj = new SomeClass();
    obj.addItem("foo");
    List<String> items = obj.getItems();
    items.add("bar");
    // Verify obj was NOT affected
    assertEquals(1, obj.getItems().size());
}
```

- Example of an **incorrect** (weak) test:
```java
@Test
public void testGetItems() {
    SomeClass obj = new SomeClass();
    obj.addItem("foo");
    assertNotNull(obj.getItems()); // Does NOT test mutation behavior
}
```