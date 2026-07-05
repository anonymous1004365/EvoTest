---
name: state-mutation-after-iteration
description: When code iterates over a collection and mutates it (adding/removing
  elements), tests must verify both the collection content and any cached/summary
  state after all iterations complete, as order of state changes vs iteration can
  create inconsistent results.
code_tags:
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# state-mutation-after-iteration

## Instructions

# State Mutation After Collection Iteration

## Instructions

- WHEN the code under test iterates over a Collection, List, Set, or Map (using for-each, iterator, or indexed loop) AND within the loop body it adds or removes elements from that same collection OR modifies related state objects,
- THEN the test MUST:
  1. Construct a test scenario where the collection has at least two elements of different types/categories.
  2. Verify that after the loop completes, the collection contains exactly the expected elements.
  3. Verify that any derived or summary state (e.g., counts, aggregated results, cached values) is consistent with the final collection content — not just that no exception was thrown.
  4. Explicitly assert on the size of the collection and the presence/absence of specific elements after mutation.

- Common pitfalls:
  - Only testing with a single-element collection, which may mask iteration-order bugs.
  - Only asserting that no exception occurs, without checking the resulting state.
  - Assuming that adding elements during iteration always appends at the end without affecting the iteration order.
  - Not testing both "add" and "remove" mutation scenarios within the same loop.

- Example (correct — testing state after mutation):

```java
// Assuming a method processElements(List<Object> list) that adds new elements during iteration
List<Object> input = new ArrayList<>();
input.add("string1");
input.add(new SomeType());
processElements(input);
// AFTER mutation, verify both size and specific content
assertEquals(3, input.size());  // one new element was added
assertTrue(input.contains("string1"));
assertTrue(input.containsAll(expectedTypes));
```

- Example (incorrect — insufficient test):

```java
List<Object> input = new ArrayList<>();
input.add("string1");
processElements(input);  // Only testing with 1 element
// No assertion on resulting collection content or size
// Bug with multi-element iteration is missed
```