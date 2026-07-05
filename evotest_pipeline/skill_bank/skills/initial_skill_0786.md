---
name: reindex-auto-flag-update-verification
description: When setting a reindex auto-flag property (`jcr:content/@reindex`), verify
  that a subsequent NodeState update is triggered which actually modifies the index
  definition. Without this, the flag is silently ignored and the index is not rebuilt.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- REINDEX_AUTO_FLAG_MISSING_UPDATE
test_pattern: STATE_TEST
---

# reindex-auto-flag-update-verification

## Instructions

# Reindex Auto-Flag Update Verification

## Instructions

- **WHEN** the code sets a property on a child of a node that controls reindex behavior (e.g., setting `reindex=true` on `jcr:content` of an index definition node), **THEN** the TG must verify that:
  1. The property value is correctly written to the underlying NodeState
  2. The resulting NodeState is properly committed/merged so the change is visible to the index update logic
  3. The index update mechanism actually reads the updated flag and performs the reindex operation

- **WHEN** the test sets `reindex=true` via `setProperty("reindex", true)` or similar on a node, **THEN** the TG must verify that after the operation, the reindex actually occurs by checking:
  - That the index definition node state contains the updated property (e.g., `getProperty("reindex")` returns `true`)
  - That the index content reflects the reindex (e.g., expected nodes appear under the index root)

- **Common pitfalls to avoid**:
  - **Testing only the property write**: Verifying `setProperty("reindex", true)` was called is not enough. You must verify the downstream effect — that the index content actually gets updated.
  - **Using a Root instance that doesn't reflect changes**: If the test merges on one Root but reads from another (or the same Root without merging), it may miss the update. Ensure the Root used for assertions has the committed changes.
  - **Forgetting to check the index content**: The key symptom of this bug is that `reindex` is set to `true` but the index remains empty (expected nodes are missing). Always check both: (a) the flag is set, AND (b) the index has the expected content.
  - **Confusing setting the flag with triggering the reindex**: Setting the flag is a precondition, not the reindex itself. The reindex is a separate operation that must be triggered by the update cycle.

### Correct example (catches the bug)

```java
// Set reindex flag
NodeBuilder indexBuilder = index.getBuilder();
indexBuilder.child("jcr:content").setProperty("reindex", true);

// Apply changes
root.commit();

// Verify the flag is set
NodeState indexState = root.getTree("/oak:index/myIndex").getNodeState();
assertTrue(indexState.getChildNode("jcr:content").getProperty("reindex").getValue(Boolean.class));

// Verify the reindex actually happened: check index content
Tree indexContent = root.getTree("/oak:index/myIndex/indexContent");
assertTrue("Index should have been rebuilt", indexContent.exists());
assertTrue("Expected node should appear after reindex", indexContent.hasChild("testRoot"));
```

### Incorrect example (misses the bug)

```java
// Set reindex flag
NodeBuilder indexBuilder = index.getBuilder();
indexBuilder.child("jcr:content").setProperty("reindex", true);

// Apply changes
root.commit();

// Only checks the flag — does NOT verify index content was rebuilt!
NodeState indexState = root.getTree("/oak:index/myIndex").getNodeState();
assertTrue(indexState.getChildNode("jcr:content").getProperty("reindex").getValue(Boolean.class));
// Bug: reindex flag is set but reindex never executed — indexContent is empty!
```