---
name: conditional-map-entry-presence-update
description: WHEN the TG encounters an UpdateOp that uses containsMapEntry as a condition
  on a map entry in a non-new document, THEN it should test that the findAndUpdate
  operation succeeds only when the condition matches the actual state of the map entry
  (existing or missing) in the stored document.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- CONDITIONAL_UPDATE_VERIFICATION
- MAP_ENTRY_PRESENCE_CHECK
test_pattern: STATE_TEST
---

# conditional-map-entry-presence-update

## Instructions

# Conditional Update with Map Entry Presence Verification

## Instructions

- WHEN the TG encounters a code path that calls `containsMapEntry(String property, Revision revision, boolean exists)` on an `UpdateOp` object (where `isNew` is `false`), and then passes that `UpdateOp` to `findAndUpdate(Collection, UpdateOp)` on a `DocumentStore`
- THEN the TG should write a test that:
  1. Creates a document in the store with a known map entry using `setMapEntry(property, revision, value)` on a new document (`new UpdateOp(path, true)`)
  2. Constructs a second `UpdateOp` with `isNew = false` containing both a change (e.g., `set("prop", "value")`) and a `containsMapEntry("map", revision, true)` condition
  3. Calls `findAndUpdate(Collection.NODES, updateOp)` and asserts that it returns a non-null document (the update succeeds because the map entry exists)
  4. Constructs a third `UpdateOp` with `isNew = false` containing a change and a `containsMapEntry("map", unknownRevision, true)` condition (where `unknownRevision` is NOT in the stored document)
  5. Calls `findAndUpdate(Collection.NODES, updateOp)` and asserts that it returns `null` (the update is rejected because the condition fails)
  6. Constructs a fourth `UpdateOp` with `isNew = false` containing a change and a `containsMapEntry("map", revision, false)` condition
  7. Calls `findAndUpdate(Collection.NODES, updateOp)` and asserts that it returns `null` (the update is rejected because the map entry DOES exist, but the condition requires its absence)
  8. After each failed conditional update, verifies that the document state was NOT modified (e.g., `prop` retains its previous value)

- WHEN the code uses `containsMapEntry` with `value = true` (EXISTS condition)
- THEN the test must use a `Revision` that is known to exist in the stored document's map entry to verify the update succeeds, and a different `Revision` (not in the map) to verify the update is rejected

- WHEN the code uses `containsMapEntry` with `value = false` (MISSING condition)
- THEN the test must verify that a `findAndUpdate` with a revision that DOES exist in the document's map entry is correctly rejected (returns null)

- Common pitfalls to avoid:
  - Calling `containsMapEntry` on a document created with `isNew = true` — the `UpdateOp.containsMapEntry` method throws `IllegalStateException` for new documents, so TG must ensure the test uses `new UpdateOp(path, false)` for conditional updates
  - Testing only one branch (EXISTS, not MISSING, or vice versa) — both `true` and `false` argument values for the `exists` parameter must be exercised
  - Forgetting to check that the document state remains unchanged after a rejected conditional update — a failed condition should leave the document intact

### Correct example (from UpdateOpTest):

```java
@Test
public void containsMapEntry() {
    Revision r = new Revision(0, 0, 0);
    Revision unknown = new Revision(0, 1, 0);
    DocumentStore docStore = openDocumentStore();
    
    // Set up: create a document with a map entry
    UpdateOp op = new UpdateOp("/node", true);
    op.setMapEntry("map", r, "value");
    docStore.createOrUpdate(Collection.NODES, op);

    // Test 1: EXISTS condition with revision that IS in the document -> succeeds
    op = new UpdateOp("/node", false);
    op.set("prop", "value");
    op.containsMapEntry("map", r, true);
    NodeDocument doc = docStore.findAndUpdate(Collection.NODES, op);
    assertNotNull(doc);  // update should succeed

    // Test 2: EXISTS condition with revision NOT in the document -> fails
    op = new UpdateOp("/node", false);
    op.set("prop", "value");
    op.containsMapEntry("map", unknown, true);
    assertNull(docStore.findAndUpdate(Collection.NODES, op));

    // Test 3: MISSING condition with revision that IS in the document -> fails
    op = new UpdateOp("/node", false);
    op.set("prop", "other");
    op.containsMapEntry("map", r, false);
    assertNull(docStore.findAndUpdate(Collection.NODES, op));

    // Verify document unchanged after failed updates
    doc = docStore.find(Collection.NODES, "/node");
    assertEquals("value", doc.get("prop"));
}
```

### Incorrect pattern to avoid:

```java
// BAD: Not testing both branches, and calling containsMapEntry on new document
UpdateOp op = new UpdateOp("/node", true);
op.containsMapEntry("map", r, true);  // throws IllegalStateException!

// BAD: Only testing positive case, not negative case
op = new UpdateOp("/node", false);
op.containsMapEntry("map", r, true);
assertNotNull(docStore.findAndUpdate(Collection.NODES, op));
// Missing: test that unknown revision causes failure

// BAD: Not verifying document state after failed conditional update
assertNull(docStore.findAndUpdate(Collection.NODES, op));
// Missing: check that prop still has its original value
```