---
name: mutation-equals-after-mutation
description: When a class overrides equals(Object) and also defines a type-specific
  equals method that overloads it (e.g., equals(Mutation)), ensure the class works
  correctly with mutable state. Verify that equals is consistent after mutation and
  that object identity is not confused with value equality during put/add/remove operations
  in collections.
code_tags:
- STATE_MUTATION
- COLLECTION_OPERATIONS
- BOOLEAN_LOGIC
- EQUALS_OVERRIDE_OVERLOAD
- OBJECT_MUTATION_METHODS
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# mutation-equals-after-mutation

## Instructions

# Mutation-Aware Equals After State Mutation

## Instructions

### WHEN you encounter a class that:
1. **Overrides `equals(Object)`** (lines ~1088 in Mutation.java)
2. **Also defines a type-specific equals overload** (e.g., `equals(Mutation m)` — ~line 1111 in Mutation.java)
3. **Has mutable state** — the object can be modified after construction via methods like `put()`, `add()`, `set()`, etc.

### THEN you MUST write tests that:

1. **Test equals consistency before and after mutation**: Create two identical mutable objects, compute `equals()` before mutation, mutate only one of them, then verify `equals()` returns `false` after the mutation.

2. **Test that put/copy/construct sequence produces correct equals**: Construct an object, copy it, then mutate the original. Verify the copy and the original are no longer equal.

3. **Test equals with `null` on the overloaded method**: Call the type-specific overload (e.g., `mutation.equals(null)`) and verify it returns `false` without throwing a `NullPointerException`.

4. **Test equals symmetry**: Verify `a.equals(b) == b.equals(a)` holds for all states (both pre-mutation and post-mutation).

### Common pitfalls to avoid:

- ❌ Testing only pre-mutation equality — mutable objects may differ after mutation even if they started identical.
- ❌ Forgetting to test the type-specific overload (`equals(Mutation m)`) separately from the `equals(Object)` override.
- ❌ Assuming that constructing two objects with the same data then mutating one does not affect equals — the mutation changes internal state tracked by equals.
- ❌ Not testing `null` on the type-specific overload — it may throw NPE instead of returning false.

### Concrete example (correct):

```java
@Test
public void testEqualsAfterMutation() {
    Mutation m1 = new Mutation(new Text("row1"));
    Mutation m2 = new Mutation(new Text("row1"));
    assertEquals(m1, m2);
    
    // Mutate m1 only
    m1.put(new Text("cf"), new Text("cq"), new Value("v1".getBytes()));
    
    // m1 and m2 should no longer be equal
    assertNotEquals(m1, m2);
    assertNotEquals(m2, m1);  // symmetry
}

@Test
public void testEqualsNullTyped() {
    Mutation m = new Mutation(new Text("row1"));
    assertFalse(m.equals(null));  // type-specific overload should handle null
}
```

### Concrete example (incorrect — too narrow):

```java
// ❌ This only tests pre-mutation equals, missing the mutation scenario
@Test
public void testEquals() {
    Mutation m1 = new Mutation(new Text("row1"));
    Mutation m2 = new Mutation(new Text("row1"));
    assertEquals(m1, m2);  // missing: mutate m1 and verify not equal
}
```