---
name: template-parameter-type-validation
description: When methods accept parameters of a generic type (e.g., Object or T) but are implemented only for a specific type (e.g., String), tests must verify correct behavior across all possible input types. This skill teaches how to catch ClassCastExceptions from unchecked casts.
code_tags: ['STATE_MUTATION', 'TYPE_CONVERSION']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts a parameter of type `Object` or a generic type `T`, and the method body contains an unchecked cast (e.g. `(String) obj` or `(SomeSpecificType) obj`) without an `instanceof` check
- THEN the TG should write a test that passes a **type that is NOT the expected cast type** to verify that the method throws a `ClassCastException` at runtime on the buggy version. For example, if the method casts to `String`, pass an `Integer` or a custom `Object`. If the method casts a lambda/closure to a specific functional interface, pass a different functional interface.
- Include concrete examples: when a `Graph.addVertices(vertices)` method internally casts each vertex to `T extends Vertex<K,V>`, test with objects that have mismatched vertex/key/value types to verify the cast fails appropriately.
- Common pitfalls:
  - Testing only with valid types (e.g., only `String` when the method also accepts non-`String` types)
  - Not testing edge cases like `null` values that could bypass the cast
  - Assuming generics provide runtime type safety — they do not. The cast is always at the developer's risk.

### Correct Example
```java
// When addVertices() casts Object to Vertex:
@Test(expected = Exception.class)
public void testAddVerticesWithInvalidType() {
    Graph<Long, Long, Long> graph = new Graph<>(...);
    // Pass Integer where Vertex is expected — should throw ClassCastException on buggy version
    graph.addVertices(Arrays.asList(42));
}
```

### Incorrect Example
```java
// WRONG — only tests valid vertex types
@Test
public void testAddVerticesWithValidType() {
    Graph<Long, Long, Long> graph = new Graph<>(...);
    Vertex<Long, Long> v = new Vertex<>(1L, 1L);
    graph.addVertices(Arrays.asList(v)); // passes but misses the bug
}
```