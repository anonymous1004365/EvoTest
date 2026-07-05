---
name: detached-state-mutation-in-branch-commits
description: When testing operations that manipulate branch commit state (e.g., removing
  uncommitted changes), the TG should verify that detached/copied state objects are
  properly isolated from the originating store, and that mutations on the copied state
  do not silently fail or corrupt the original store state.
code_tags:
- STATE_MUTATION
- CONCURRENCY
- BRANCH_COMMIT_STATE
test_pattern: STATE_TEST
---

# detached-state-mutation-in-branch-commits

## Instructions

# Detached State Mutation in Branch Commits

## Instructions

- WHEN the TG encounters code that creates a **detached or copied state object** from a store (e.g., a `Branch` instance obtained via `store.createBranch(b)`, a `Commit` obtained from a `DocumentNodeStore`, or any object whose lifecycle is semi-independent from its creator)
- THEN the TG should write a test that:
  1. Acquires the detached state object (e.g., the `Branch`).
  2. Mutates the state object in a way that should be persisted (e.g., calling `branch.removeUncommitted(commitRoot)` or `branch.purge(…)`).
  3. **Verifies that the mutation actually took effect** — e.g., by later checking the same state object for the expected side-effect (like the commitRoot being removed).
  4. Also verifies that the store-level state is consistent (e.g., no orphaned branches remain).

- **Common pitfall**: Testing only that a method *returns without error* when called on a detached/copied state object, without verifying that the mutation **actually changed the object's internal state**. A method might silently accept a call but not mutate the underlying data structure.

- **Example of a correct test** (for `removeUncommitted` on a Branch obtained from a store):

```java
// Correct: Verify the mutation actually took effect on the Branch object
Branch branch = store.createBranch(b);
// mutate: e.g., branch.removeUncommitted(someCommitRoot);
// Then assert that the internal state changed:
//   assertNull("commitRoot should have been removed", branch.getCommitRoot());
```

- **Example of an incorrect test** (no state verification):

```java
// INCORRECT: Only tests that calling the method doesn't throw
Branch branch = store.createBranch(b);
branch.removeUncommitted(someCommitRoot);  // No assertion about branch state
// The test could pass even if removeUncommitted silently did nothing
```

- **Additional considerations**: When the state object is backed by a concurrent or shared data structure (like a `CommitQueue` or `Map<Revision, Range>`), also verify that the operation is **idempotent** and that calling it multiple times does not cause corruption (e.g., no `ConcurrentModificationException`, no `NullPointerException`, no data leaks).