---
name: cancelable-diff-child-node-changed-safety
description: When a diff traversal (like CancelableDiff) delegates childNodeChanged
  callbacks that can throw exceptions, the compactor/editor must ensure the diff state
  is properly reset before reusing it. Use this skill to write tests that verify the
  compactor correctly handles failures during child node compaction.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONDITIONAL_BRANCH
test_pattern: INTERACTION_TEST
---

# cancelable-diff-child-node-changed-safety

## Instructions

# CancelableDiff ChildNodeChanged Safety

## Instructions

- WHEN the TG encounters a compaction/diff mechanism where a `CancelableDiff` is used to traverse a tree structure and its `childNodeChanged`, `childNodeAdded`, or `childNodeDeleted` methods are called by an `Editor` (e.g., a `Compactor`), and a `SegmentWriter` can be configured to throw exceptions for specific node names
- THEN the TG should write a test that:
  1. Creates a fake/mock `SegmentWriter` (e.g., `FailingSegmentWriter`) that throws an exception (e.g., `IOException` wrapped in `RuntimeException`) when writing a segment for a specific node name (e.g., `"child0"`).
  2. Constructs a tree with at least two child nodes under the root (e.g., `"test0"` and `"child0"`), where one of them triggers the exception.
  3. Invokes the compaction process (e.g., `compactor.compact(...)`) and verifies the result.
  4. Verifies that **all successfully processed nodes before the failure** are preserved in the result, and nodes after the failure are absent (the expected state should reflect partial compaction rather than a blank/empty state).
  5. The test should expect an exception (e.g., `RuntimeException` or `IOException`) to be thrown during compaction, NOT a successful result — unless the fix changes behavior to swallow the exception.
- **Common pitfalls to avoid**:
  - ❌ Testing only a single child node — this will not catch the bug because the bug manifests when some nodes succeed and others fail during the same compaction run.
  - ❌ Testing only with `childNodeAdded` or `childNodeDeleted` — the bug specifically involves `childNodeChanged` being called on a diff that may have been left in an inconsistent state after a previous call throws.
  - ❌ Forgetting to check the actual state of the resulting `NodeState` — a passing test must assert that the compaction output is not empty/blank on the fixed version.
  - ❌ Using a real `SegmentWriter` that never fails — the test must induce a controlled failure at a specific node name.
- **Correct example**: Create a tree with root → `"test0"` (leaf) and `"child0"` (leaf). Make the `FailingSegmentWriter` fail when asked to write `"child0"`. Compact. Assert that the compaction throws an exception, and that the resulting state does NOT contain `"test0"` (since `test0` was never reached due to the failure — or it could be missing depending on the fix). On the **fixed** version, the diff's internal state is properly reset so the compaction doesn't leave the `NodeBuilder` in a blank state.
- **Incorrect example**: Creating a test that only calls `childNodeChanged` manually on the diff object without going through the full compaction pipeline — the bug may not be triggered unless the actual `Compactor.compact(...)` flow is exercised with a realistic tree structure containing multiple child nodes.