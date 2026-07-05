---
name: updateop-key-equals-contract
description: When the custom Key class inside UpdateOp uses 'property' + 'revision'
  fields in equals(), the hashCode() must be consistent. Test equals() with various
  combinations of same/different property names and Revision instances (including
  null revisions) to verify symmetry, reflexivity, and hashCode consistency.
code_tags:
- EQUALS_HASHCODE_CONTRACT
- NULL_CHECK
test_pattern: STATE_TEST
---

# updateop-key-equals-contract

## Instructions

# UpdateOp.Key Equals Contract Test

## Instructions

- WHEN the TG encounters a custom `Key` nested class (e.g., `UpdateOp.Key`) that has fields `property` (String) and `revision` (Revision, nullable), and is used as a HashMap key in a `Map<Key, Operation>`
- THEN it should write tests that verify the `equals()` contract and `hashCode()` consistency:
  1. **Different property, same revision**: Create two keys with different property names (e.g., "foo" vs "bar") and the same revision value (including null). Assert `k1.equals(k2)` is `false` and `k2.equals(k1)` is `false`.
  2. **Same property, same revision**: Create two keys with the same property name (e.g., "foo") and the same revision value (including null). Assert `k1.equals(k2)` is `true` and `k2.equals(k1)` is `true`.
  3. **Same property, different revision instances**: Create two keys with the same property name and two *different* Revision instances (e.g., `Revision r1 = Revision.newRevision(1)` and `Revision r2 = Revision.newRevision(1)` — same cluster but different objects). Assert `k1.equals(k2)` is `true` when revisions are logically equal, or test that a Key with revision `r1` is NOT equal to a Key with revision `null`, and vice versa.
  4. **Symmetry**: For every pair of keys, verify both `k1.equals(k2)` and `k2.equals(k1)`.
  5. **Implicit HashMap usage**: Test that keys with equal revisions (different Revision instances with same logical value) and same property can be looked up in a HashMap. For example, `map.put(new Key("foo", r1), value); assertSame(value, map.get(new Key("foo", r2)));`

- Common pitfalls:
  - Testing only String-typed parameters and not testing with `Revision` parameters.
  - Not testing with `null` revision values (keys can be created with `new Key(property, null)` when no revision is needed).
  - Testing the equals() method directly but not testing the implied HashMap behavior (e.g., put followed by get using a logically equal key).
  - Not testing both directions of equals (asymmetry bug).
  - Assuming two different Revision objects created with the same parameters are `equals()` — verify the Revision class's equals behavior first.

### Correct example:
```java
@Test
public void keyEquals() {
    Revision r1 = Revision.newRevision(1);
    Revision r2 = Revision.newRevision(1);

    UpdateOp.Key k1 = new UpdateOp.Key("foo", null);
    UpdateOp.Key k2 = new UpdateOp.Key("bar", null);
    assertFalse(k1.equals(k2));
    assertFalse(k2.equals(k1));

    UpdateOp.Key k3 = new UpdateOp.Key("foo", null);
    assertTrue(k1.equals(k3));
    assertTrue(k3.equals(k1));
    
    UpdateOp.Key k4 = new UpdateOp.Key("foo", r1);
    assertFalse(k4.equals(k3));
    assertFalse(k3.equals(k4));
    
    UpdateOp.Key k5 = new UpdateOp.Key("foo", r2);
    assertTrue(k5.equals(k4));  // revisions may be logically equal
    assertTrue(k4.equals(k5));
    
    UpdateOp.Key k6 = new UpdateOp.Key("bar", r1);
    assertFalse(k6.equals(k4));
    assertFalse(k4.equals(k6));
}
```

### Incorrect example (what to avoid):
```java
//❌ ONLY tests String keys without covering Revision/null cases
@Test
public void keyEquals() {
    UpdateOp.Key k1 = new UpdateOp.Key("foo", null);
    UpdateOp.Key k2 = new UpdateOp.Key("foo", null);
    assertTrue(k1.equals(k2)); // only tests simplest case
}
```