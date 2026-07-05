---
name: collection-type-param-type-check
description: When a collection or map field stores mixed types (e.g., Object or Comparable),
  test that elements of all relevant types are correctly accepted and persisted. This
  prevents bugs where adding mismatched types corrupts internal state.
code_tags:
- ARGUMENT_VALIDATION
- BEAN_PROPERTY_ASSIGNMENT
- NULL_CHECK
test_pattern: STATE_TEST
---

# collection-type-param-type-check

## Instructions

# Collection Type Parameter Validation

## Instructions

- WHEN the TG encounters a **collection, map, or array-typed field** whose generic type parameter is **`Object`**, **`Comparable`**, **`Serializable`**, or another non-specific type that could accept multiple different concrete types — AND the collection is used as a property that stores values from user input or external sources
- THEN the TG should write a test that **adds elements of different concrete types** (e.g., `String`, `Integer`, custom POJO) to that collection via the public API, then **verifies the collection retains all elements correctly** after serialization/deserialization or state persistence
- Include at least **two different element types** that share the declared generic type (e.g., a `String` and an `Integer` for a `List<Comparable>`; a `Map<String, Object>` with both `String` and numeric values)
- Verify correctness by asserting the collection **contains** the added elements and that retrieving them returns the **same type and value**
- **Common pitfalls to avoid:**
  - Testing only one type of element (e.g., only `String`) when the parameter type allows multiple types — this masks mixed-type bugs
  - Forgetting that **primitive boxing** can change type semantics (e.g., `int` becomes `Integer`, which is a different `Object` subtype than `String`)
  - Assuming the collection's internal representation (e.g., `Array` vs `List`) is irrelevant — bugs often arise when serialization/deserialization or deep-copy logic mishandles mixed types
  - Not checking that the collection **size** is correct after adding mixed types

### Correct Example (should pass on fixed code)

```java
// Test that a List<Object> (or similar) property accepts and retains mixed types
@Test
public void testMixedTypesInCollectionProperty() {
    MyBean bean = new MyBean();
    List<Object> list = new ArrayList<>();
    list.add("hello");
    list.add(42);
    bean.setItems(list);
    
    // e.g., serialize and deserialize, or just verify state
    assertEquals(2, bean.getItems().size());
    assertEquals("hello", bean.getItems().get(0));
    assertEquals(42, bean.getItems().get(1));
}
```

### Incorrect Example (would miss the bug)

```java
// Only tests String type — would NOT catch a bug where Integer elements break internal state
@Test
public void testListProperty() {
    MyBean bean = new MyBean();
    List<Object> list = new ArrayList<>();
    list.add("hello");
    bean.setItems(list);
    
    assertEquals(1, bean.getItems().size());
    assertEquals("hello", bean.getItems().get(0));
}
```