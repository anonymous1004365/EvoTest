---
name: children-flag-during-document-split
description: WHEN splitting documents that have a commit root with children, THEN
  the test must verify that the CHILDREN_FLAG is properly preserved/copied onto the
  new split document, otherwise child documents may incorrectly appear to have no
  children.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# children-flag-during-document-split

## Instructions

# Preserve Children Flag During Document Split

## Instructions

- WHEN the system performs a **document split operation** (splitting a document into an intermediate document + original document) and the document has a `COMMIT_ROOT` field pointing to a commit root,
- THEN the test must verify that the **children flag** (`NodeDocument.CHILDREN_FLAG`) is **properly preserved/copied onto the new split/intermediate document** — specifically, if the original document had `CHILDREN_FLAG` set to `true`, the split document must also have `CHILDREN_FLAG` set to `true`.

- **Concrete values**: `NodeDocument.CHILDREN_FLAG` is a `Boolean` field fetched via `get(CHILDREN_FLAG)`. The flag is `true` when a node has children, and the method `NodeDocument.hasChildren()` checks `getChildrenFlag()` which does: `Boolean childrenFlag = (Boolean) get(CHILDREN_FLAG); return childrenFlag != null && childrenFlag;`

- The test should:
  1. Create a document with `CHILDREN_FLAG` set to `true` and a `COMMIT_ROOT` pointing to a specific commit root (e.g., a revision like `r0-0-1`).
  2. Perform the split operation (e.g., via `DocumentSplit.split()`) which processes documents and splits those with commit roots.
  3. After the split, retrieve the **intermediate/previous document** (the `@previous` document or the document the original pointed to via its commit root).
  4. Assert that the intermediate/previous document's `hasChildren()` method returns `true`.
  5. Also assert that the original document (after split) still correctly reflects its own children.

- **Common pitfalls**:
  - Testing only the existence of the children flag on the original document after split, without checking the **new split/intermediate document** that was created.
  - Assuming that the children flag is irrelevant during split because "the commit root is being split away" — the children flag must be carried over to the intermediate document.
  - Testing with documents that don't have a `COMMIT_ROOT` set, which won't trigger the splitting code path that contains this bug.
  - Forgetting to set up the revision context properly (e.g., using `Revision.newRevision()` or specific revision IDs) so that the commit root condition is met.

- **Correct example**:
```java
// Create document with children flag and commit root
String id = "test-node";
NodeDocument doc = createDocumentWithData(store, id, 2 /*num children*/);
// ...
// Set commit root on a child revision
String commitRootRev = "r0-0-1";
// ... perform split
splitter.split();
// Verify intermediate document has children flag
NodeDocument prevDoc = store.find(NODES, id + "@previous");
assertNotNull(prevDoc);
assertTrue("Previous document must have children flag", prevDoc.hasChildren());
```

- **Incorrect example** (would NOT catch the bug):
```java
// Only checks original document, not the intermediate split document
splitter.split();
NodeDocument doc = store.find(NODES, id);
assertTrue("Original doc should still have children after split", doc.hasChildren());
// Bug: the intermediate (previous) document lost its children flag
// but the test never checks it
```