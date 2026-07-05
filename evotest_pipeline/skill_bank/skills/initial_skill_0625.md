---
name: commit-apply-failure-state-consistency
description: When a commit method applies changes to a document store via findAndUpdate
  operations that may fail partway through, test that the commit properly cleans up
  partial state (rollback) and that subsequent operations see a consistent view. Relevant
  when a DocumentStore is used with in-memory or mock stores that simulate failures.
code_tags:
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: INTERACTION_TEST
---

# commit-apply-failure-state-consistency

## Instructions

# Commit Apply Failure and State Consistency

## Instructions

WHEN the code under test implements a commit/apply pattern that updates multiple documents via `findAndUpdate` (e.g., updating commit root documents and node documents), and the update operations can include a "final commit root update" (identified by having only `_revisions` and `_modified` entries in its changes):

- THEN create a test using a custom `MemoryDocumentStore` (or equivalent mock) that overrides `findAndUpdate` to:
  1. Allow normal updates for all operations except the final commit root update.
  2. Throw a `RuntimeException` (e.g., `new RuntimeException("communication failure")`) when the final commit root update is detected.
  3. Use an `AtomicBoolean` flag (e.g., `throwAfterUpdate`) to control when the exception is triggered — set it `true` before the commit, `false` otherwise.
  4. Detect the "final commit root update" by inspecting the UpdateOp's changes map: iterate over the entries and check if every key name is either a revisions entry (`NodeDocument.isRevisionsEntry(name)`) or `NodeDocument.MODIFIED_IN_SECS`. If so, it is the final commit root update.

- WHEN performing the commit:
  1. Call `nodeStore.newCommit(headRevision, null)` to get a `Commit` object.
  2. Add multiple nodes to the commit (e.g., `c.addNode(new DocumentNodeState(ns, "/foo/node", c.getBaseRevision()))` and similarly for `/bar/node`).
  3. Call `c.apply()` inside a try block.
  4. In the `finally` block, differentiate success vs. failure: if `apply()` succeeded, call `ns.done(c, false, CommitInfo.EMPTY)`; if it failed (caught an exception), call `ns.canceled(c)`.

- THEN verify:
  - On the **buggy version**, after the exception on the final commit root update, the node store state may be inconsistent: some nodes might not appear in the root state, or the `AtomicBoolean` flag may still be `true` (indicating the exception was never thrown or the cleanup failed).
  - On the **fixed version**, the commit state should be consistent: all added nodes should exist in the root state (e.g., `root.getChildNode("foo").getChildNode("node").exists()` returns `true`), and the `AtomicBoolean` flag should be `false` (the exception was thrown and the state was correctly rolled back).

- AVOID common pitfalls:
  - Do NOT simply verify that an exception was thrown — you must verify the **consistency of the final state** after the failure was handled.
  - Do NOT test with only a single node addition — test with multiple nodes to catch partial-update bugs.
  - Do NOT forget to set `setAsyncDelay(0)` on the builder to ensure synchronous operations.
  - Do NOT forget to call both `ns.newCommit()` AND handle `done`/`canceled` correctly — the bug is in how the commit's state (specifically the commit root's `_modCount`) is managed when `apply()` fails partway through.