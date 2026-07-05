---
name: collection-modification-during-iteration
description: When a method modifies a collection while another process is iterating
  over it, the TG should use STATE_TEST to verify consistent snapshots. The triggering
  test PipelineTests.basicUsage demonstrates silent failure where pipeline processing
  modifies shared mutable state during iteration, causing non-deterministic bugs.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# collection-modification-during-iteration

## Instructions

# Collection Modification During Iteration

## Instructions

- WHEN the TG encounters code that iterates over a mutable collection (e.g., via for-each, Iterator, or stream) and, during iteration, calls methods that may modify the same collection (add, remove, put, clear)
- THEN it should write a test that:
  1. Creates a shared mutable collection (e.g., ArrayList, HashMap) with initial elements
  2. Passes this collection to a method/processor that iterates over it
  3. During iteration, exercises code paths that may mutate the collection (e.g., by processing elements that trigger cascading mutations)
  4. Asserts that the iteration completes without throwing ConcurrentModificationException AND that either the iteration uses a defensive snapshot (copy) or the mutation is safe (e.g., uses ListIterator.remove())
  5. If the buggy version silently produces corrupt/partially-processed data, verify the output matches expected results exactly

- Common pitfalls:
  - Testing only with empty collections (mutation during iteration won't trigger)
  - Testing only with collections that have 1 element (the iteration terminates before the mutation matters)
  - Using thread-safe collections (like CopyOnWriteArrayList) which mask the bug
  - Assuming ConcurrentModificationException is the only symptom — many bugs silently produce wrong results when iterators detect modifications inconsistently

- Correct example (detecting the bug):
  ```java
  @Test
  void testModificationDuringIteration() {
      // Arrange
      List<String> items = new ArrayList<>(Arrays.asList("a", "b", "c", "d"));
      Pipeline pipeline = new Pipeline(items);
      
      // Act — this should either succeed with a correct snapshot or fail cleanly
      List<String> result = pipeline.processAll();
      
      // Assert — the buggy version may silently drop or duplicate elements
      assertEquals(4, result.size(), 
          "All original elements should be present");
      assertTrue(result.containsAll(Arrays.asList("a", "b", "c", "d")),
          "Result should contain all original elements");
  }
  ```

- Incorrect example (masking the bug):
  ```java
  @Test
  void testEmptyCollection() {
      Pipeline pipeline = new Pipeline(new ArrayList<>());
      List<String> result = pipeline.processAll();
      assertTrue(result.isEmpty());  // Bug never triggered
  }
  ```