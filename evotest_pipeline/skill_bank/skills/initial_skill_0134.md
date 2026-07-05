---
name: unmerged-commit-state-purge
description: When code purges uncommitted revisions or collision markers from documents
  that are part of unmerged branches, the TG should test that the overall merge/purge
  logic correctly handles overlapping uncommitted state between commits. This skill
  applies to scenarios where internal state management for uncommitted data must be
  correctly isolated between separate merge attempts.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# unmerged-commit-state-purge

## Instructions

# Purge of Unmerged Commit State

## Instructions

- **WHEN** a method purges **uncommitted revisions** or **collision markers** from documents (e.g., `purgeUncommittedRevisions(RevisionContext)` and `purgeCollisionMarkers(RevisionContext)` on `NodeDocument`) **AND** those documents belong to a collection of unmerged branches (e.g., `UnmergedBranches`),
- **THEN** the TG should write a test that:
  1. Creates a document with **uncommitted changes** (revisions) and **collision markers** present on it.
  2. Adds that document to an **unmerged branches** container (e.g., `UnmergedBranches`).
  3. Calls the **purge** operation (e.g., `purgeUnmergedBranch()` or equivalent) that triggers both `purgeUncommittedRevisions()` and `purgeCollisionMarkers()` on the document.
  4. **Verifies** that after the purge, the uncommitted revisions and collision markers are removed **and** that subsequent merge/purge operations do not fail or double-count — specifically, if the purge is called again on the same (already purged) `UnmergedBranches` instance, it should **not** throw an exception (e.g., `IllegalStateException`) and should return zero or consistent counts.
  5. **Verifies** that the document's internal state after purge does not retain stale uncommitted revision data that could cause incorrect behavior on later commits.

- **Common pitfalls to avoid**:
  - ❌ **Testing only the first purge call** without verifying that a **second call** on the same branch collection works correctly (the bug may manifest on re-purge of already-purged state).
  - ❌ **Not setting up both uncommitted revisions AND collision markers** — the interaction between them can trigger the bug.
  - ❌ **Testing `purgeUncommittedRevisions()` in isolation** without the `UnmergedBranches` wrapper that triggers both purge methods sequentially — the bug may only surface when both operations run together on the same document.
  - ❌ **Assuming that clearing the document's uncommitted state in one step makes subsequent steps safe** — the internal collection (e.g., `Set<Revision>`) may have been mutated such that iteration over it during the first purge leaves it in an inconsistent state for a second call.

- **Concrete example (correct)**:
  ```java
  // Given a document with uncommitted revisions and collision markers
  NodeDocument doc = ...; // setup with uncommitted revisions + collision markers
  
  // Given an UnmergedBranches instance containing that document
  UnmergedBranches branches = new UnmergedBranches(...);
  branches.add(doc);
  
  // When purging the branch the first time — should succeed
  branches.purge(); // internally calls doc.purgeUncommittedRevisions() + doc.purgeCollisionMarkers()
  
  // When purging the same branch a second time — should NOT throw
  branches.purge(); // Bug: could throw IllegalStateException because internal state was already consumed
  ```

- **Concrete example (incorrect)**:
  ```java
  // ❌ Bad: Only tests the first purge call
  branches.purge();
  // Missing: verify second purge does not fail
  ```