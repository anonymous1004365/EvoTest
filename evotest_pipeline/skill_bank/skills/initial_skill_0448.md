---
name: hashcode-consistency-for-mutable-collections
description: When a class overrides hashCode() or equals() and contains collection
  fields whose elements have mutable hashCode() behavior, tests must verify hash-based
  collection usage does not produce unexpected behavior on the buggy version. This
  skill applies to classes that add elements to HashSets or HashMaps and whose elements
  have mutable state affecting hashCode().
code_tags:
- NULL_CHECK
- VALIDATION
- HASH_CODE_EQUALS
- DATA_STRUCTURE_MODIFICATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# hashcode-consistency-for-mutable-collections

## Instructions

# hashCode Consistency for Mutable Collection Elements

## Instructions

WHEN the TG encounters a class that:
- Overrides `hashCode()` and/or `equals()` methods
- Adds objects to a `HashSet`, `HashMap`, or other hash-based collection
- The objects added to the collection have mutable state that is used in their `hashCode()` calculation (e.g., the objects belong to a class hierarchy with subclasses having different fields)

THEN the TG should write a test that:
1. Creates instances of different subclasses/types that are added to a hash-based collection
2. Verifies that the hash-based collection behaves consistently (e.g., contains() returns true after adding)
3. Specifically tests that all added instances are properly contained in the collection after construction/initialization
4. If the code adds elements to a HashSet and there's a `hashCode()` or `equals()` contract issue between related types, the test should verify that:
   - All elements are present in the set after construction
   - The set size is correct
   - Iterating the set yields all expected elements

Common pitfalls to avoid:
- Testing only one type/subclass of elements when multiple types are stored in the collection
- Assuming that if `add()` succeeds, `contains()` will return true — this can fail if `hashCode()`/`equals()` is inconsistent between types
- Not testing the scenario where related types (e.g., parent and child classes, or different implementations of an interface) are stored together in a hash-based collection

### Example (correct approach)

```java
// Correct: Tests that all operand types are properly contained in the set
@Test
public void testHashCode() {
    Set<Operand> operands = new HashSet<>();
    
    // Create instances of different operand types
    Operand operand1 = new Operand(new DataElement("A"), null);
    Operand operand2 = new Operand(new DataElement("B"), "category1");
    Operand operand3 = new Operand(new DataElement("C"), null);
    
    operands.add(operand1);
    operands.add(operand2);
    operands.add(operand3);
    
    // Verify all elements are contained
    assertTrue(operands.contains(operand1));
    assertTrue(operands.contains(operand2));
    assertTrue(operands.contains(operand3));
    assertEquals(3, operands.size());
}
```

### Example (incorrect approach — fails to detect this bug)

```java
// Wrong: Only tests one type of operand, misses hashCode/equals inconsistencies
@Test
public void testHashCode() {
    Operand operand = new Operand(new DataElement("A"), null);
    Set<Operand> set = new HashSet<>();
    set.add(operand);
    assertTrue(set.contains(operand));  // Works with one element, misses cross-type issues
    assertEquals(1, set.size());
}
```

### Additional Guidance

- When `hashCode()` uses `Objects.hash()` with multiple fields, ensure the test covers field combinations that could produce collisions or inconsistencies
- Pay special attention when `equals()` checks `getClass()` equality while `hashCode()` is inherited or uses a different type check — this creates an asymmetry that breaks hash-based collections
- For Operand-like patterns where different sub-flavors share a common parent, test that they can coexist in the same HashSet without violating the hashCode contract