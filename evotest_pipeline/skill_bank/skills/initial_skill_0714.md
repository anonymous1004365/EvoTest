---
name: iteration-resource-cleanup-on-close
description: When a resource-holding iteration or loop structure is closed/terminated,
  the test must verify that internal state (e.g., buffers, iterators, queues) is properly
  cleaned up to avoid stale state affecting subsequent operations. This is critical
  for iterative operators in stream processing frameworks.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# iteration-resource-cleanup-on-close

## Instructions

# Iteration Resource Cleanup on Close

## Instructions

- WHEN the TG encounters an iterative operator or loop construct that holds internal state (e.g., buffers, iterators, queues, lists of feedback edges)
- THEN it MUST verify that when the iteration is closed/terminated, all internal state is properly cleaned up
  - Specifically, check that calling close() or terminate() on the iteration clears internal collections, especially those tracking feedback edges or output partitions
  - Use reflection or accessor methods if the collections are private, OR test behaviorally by verifying no side effects remain after close
- Common pitfalls to avoid:
  - Testing only the happy path where iteration completes normally, without verifying cleanup
  - Assuming that garbage collection handles the cleanup
  - Not testing that a second iteration or operation after close() uses fresh state

Example correct test:
```java
@Test
public void testIterationStateCleanupOnClose() {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> source = env.fromElements(1, 2, 3);
    IterativeStream<Integer> iteration = source.iterate(5000);
    // ... set up iteration body ...
    iteration.close();
    
    // Verify that after close, no stale feedback state remains
    // e.g., check that internal feedback edge list is empty
    // (specific assertion depends on the implementation)
    
    // Also verify that the environment can be reused for new iterations
    DataStream<Integer> newSource = env.fromElements(4, 5, 6);
    IterativeStream<Integer> newIteration = newSource.iterate(5000);
    // Should not throw due to stale state from previous iteration
}
```

Example incorrect test (missing cleanup verification):
```java
@Test
public void testIterationHappyPath() {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<Integer> source = env.fromElements(1, 2, 3);
    IterativeStream<Integer> iteration = source.iterate(5000);
    // ... set up iteration body ...
    iteration.close();
    // Does NOT verify internal state cleanup
    // Buggy version may retain stale state causing issues on subsequent operations
}
```