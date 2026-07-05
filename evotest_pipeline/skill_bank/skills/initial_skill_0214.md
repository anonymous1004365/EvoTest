---
name: collection-mutation-during-iteration
description: When iterating over a collection while conditionally removing elements
  via an iterator, test that elements are correctly removed and that no ConcurrentModificationException
  or missed removals occur. Use parametric testing with different collection states
  to verify correct iteration behavior.
code_tags:
- STATE_MUTATION
- CONDITIONAL_BRANCH
- EDGE_CASE_INPUT
test_pattern: PARAMETRIC_TEST
---

# collection-mutation-during-iteration

## Instructions

# Collection Mutation During Iteration

## Instructions

- WHEN the TG encounters code that iterates over a mutable collection (e.g., `List`, `Set`, `Map`) and conditionally removes elements during iteration using `Iterator.remove()` or by building a new collection
- THEN it must write tests that exercise:
  1. **Removal boundary conditions**: removing the first element, the last element, adjacent elements, and no elements
  2. **The boolean condition used to decide removal**: test with inputs that make the condition true and false for different elements in the collection
  3. **The collection state before and after**: verify that the collection size and contents after iteration match the expected surviving elements
- Include verifications that:
  - No `ConcurrentModificationException` is thrown (proving iterator-based removal is safe)
  - The exact set of expected elements remains after the operation
  - Elements that should have been removed are actually gone
- Common pitfalls to avoid:
  - Testing only one removal scenario — the bug may only appear when removing specific elements (e.g., the first or last) or when removing multiple elements
  - Forgetting to verify the contents of the collection after mutation, not just the size
  - Using `for-each` loops in the test code itself when testing removal logic that uses iterators (the test should use explicit iterators to match the code under test)