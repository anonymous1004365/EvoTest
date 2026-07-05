---
name: document-node-store-null-entry-read
description: When testing DocumentNodeStore's getNodeState() for a path whose document
  contains a null entry in its map of node revision histories, verify that the method
  returns null (no state) rather than reading stale previous documents. This prevents
  stale/incorrect NodeState from being returned after a node has been removed.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# document-node-store-null-entry-read

## Instructions

# Read Null Entry From DocumentNodeStore

## Instructions

### WHEN the TG encounters code that uses `DocumentNodeStore` or `NodeDocument` to retrieve a `NodeState` via a path, and there exists a scenario where a document has a null entry in its revisions map (e.g., the result of a node being removed after a previous modification):

- **THEN** the test should:
  1. Create a `DocumentNodeStore` instance (e.g., via `new DocumentMK.Builder().setAsyncDelay(0).getNodeStore()`).
  2. Add a child node (e.g., `builder.child("test")`), then merge the change.
  3. Get a child `NodeState` from the root (e.g., `store.getRoot().getChildNode("test")`).
  4. Remove that child node from the builder (e.g., `builder.child("test").remove()`), then merge the removal.
  5. After the removal, get a fresh `NodeState` from the store (e.g., `store.getRoot().getChildNode("test")`).
  6. **Verify** that the returned `NodeState` after removal is `null` (i.e., assertNull).
  7. Additionally, if the store exposes `getNodeState(Path, lastRevs)`, call it directly with a `Path` for a removed node and verify it returns `null` rather than returning some stale prior document state.

- **Common pitfalls to avoid:**
  - Do NOT assume `getChildNode("test")` returns null just because the node was removed — the internal `DocumentNodeStore.getNodeState()` might return a stale state if it reads from previous documents due to a null entry in the revisions map. The test must assert that the state after removal is truly null.
  - Do NOT forget to call `store.getRoot()` (fresh root) after the removal merge — the test must use the latest root to confirm the removal is visible.
  - Do NOT test only that the node "exists then does not exist" using `hasChildNode()` — the bug manifests when `getChildNode()` is called and returns a stale non-null state even though the node was removed. Use `getChildNode()` and assertNull on the returned state.
  - Do NOT skip the intermediate step of getting a child state before removal — the null entry bug only manifests after a child state was previously read (which sets up a null entry in the map).

### Example (correct):

```java
public void readNullEntry() throws CommitFailedException {
    DocumentNodeStore store = new DocumentMK.Builder()
            .setAsyncDelay(0).getNodeStore();
    NodeBuilder builder = store.getRoot().builder();
    builder.child("test");
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

    // get child state — this creates an entry in revisions map
    NodeState before = store.getRoot().getChildNode("test");
    assertNotNull(before);

    // remove the child
    builder = store.getRoot().builder();
    builder.child("test").remove();
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);

    // after removal, must return null
    NodeState after = store.getRoot().getChildNode("test");
    assertNull("must not read previous document", after);

    store.dispose();
}
```

### Example (incorrect — fails to catch the bug):

```java
public void readNullEntry() throws CommitFailedException {
    DocumentNodeStore store = new DocumentMK.Builder()
            .setAsyncDelay(0).getNodeStore();
    NodeBuilder builder = store.getRoot().builder();
    builder.child("test");
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);
    
    // Only tests hasChildNode, which may hide the bug
    assertTrue(store.getRoot().hasChildNode("test"));
    
    builder = store.getRoot().builder();
    builder.child("test").remove();
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);
    
    // hasChildNode might return false but getChildNode still returns stale state
    assertFalse(store.getRoot().hasChildNode("test"));
    
    store.dispose();
}
```