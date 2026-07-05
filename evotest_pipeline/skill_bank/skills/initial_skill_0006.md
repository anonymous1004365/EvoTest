---
name: node-locator-immutable-equality
description: When implementing value objects with immutable-like semantics, test that
  equals() defends against mutation of internal state by different parameter types
  and ensures equality holds across type-consistent construction paths.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# node-locator-immutable-equality

## Instructions

# NodeLocator Immutable Equality Validation

## Instructions

- WHEN the TG encounters a value/immutable class (e.g., `NodeLocator`) that is constructed from multiple parameter types (e.g., `String` endpoint, `Long` nodeId), and the class implements `equals()` for value-based comparison:
  - THEN it should construct two objects using different equivalent inputs (e.g., one from parsed `String` representation, one from explicit typed parameters) and verify they are equal via `assertEquals(obj1, obj2)` and `assertEquals(obj1.hashCode(), obj2.hashCode())`.
  - It should also verify that the class does **not** accidentally mutate its internal state based on the input type during construction (e.g., a `String` constructor should not transform data in a way that yields different internal fields compared to a typed constructor).
  - It must test **at least two distinct construction paths** that should produce semantically identical objects, and assert their equality.

- WHEN the triggering test indicates failure in equality checks between objects created via different construction paths:
  - THEN the TG should inspect the class's `equals()` and `hashCode()` methods, as well as any conversion/parsing logic inside constructors or factory methods, for bugs that cause logically equal objects to differ.
  - Common pitfalls:
    - Testing only the same construction path (e.g., `new NodeLocator("tcp://localhost:9000")` vs `new NodeLocator("tcp://localhost:9000")`) — this misses bugs arising from **different input types**.
    - Assuming `equals()` works correctly for all inputs without testing cross-type construction equality.
    - Not running the test against the **buggy** version to verify it fails with the expected assertion error before the fix.

- **Correct example** (targets the bug):
  ```java
  @Test
  public void testStringWithIdIsEqual() {
      NodeLocator fromString = NodeLocator.fromString("tcp://localhost:9000");
      NodeLocator fromTyped = new NodeLocator("localhost", 9000);
      assertEquals("String-constructed and typed-constructed NodeLocators should be equal",
          fromString, fromTyped);
  }
  ```

- **Incorrect example** (misses the bug):
  ```java
  @Test
  public void testStringConstruction() {
      NodeLocator locator = NodeLocator.fromString("tcp://localhost:9000");
      assertEquals("localhost", locator.getHost());
      assertEquals(9000, locator.getPort());
  }
  ```