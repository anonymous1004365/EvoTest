---
name: document-store-visibility-modcount-synchronization
description: When testing concurrent updates to DocumentStore documents, tests must
  verify that _modCount strictly increases across visibility changes, and that synchronization
  on the document ID ensures correct ordering. Use this skill when validating atomic
  counter behavior under concurrent access.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# document-store-visibility-modcount-synchronization

## Instructions

# DocumentStore Visibility _modCount Strict Increase Verification

## Instructions

- WHEN the TG encounters a `DocumentStore` with methods `createOrUpdateDoc(Collection<UpdateOp>)` and/or `getVisibility()` or visibility-related state that updates a `_modCount` field on documents
- THEN the TG should write a test that:
  1. Creates a document with an initial `_modCount` value (typically 1 or 2)
  2. Reads the document to capture `ds1Mc = (Long) doc.get("_modCount")`
  3. Calls `setVisibility(...)` (or equivalent visibility-changing operation) on the document store
  4. Reads the document again from **another DocumentStore instance sharing the same underlying store** to capture `ds2Mc = (Long) doc.get("_modCount")`
  5. Asserts `assertTrue("_modCount needs to be > " + origMc + " but was " + ds2Mc, ds2Mc > origMc)`
  6. Asserts the reverse direction as well when changing visibility back: `assertTrue("_modCount needs to be > " + ds2Mc + " but was " + ds1Mc, ds1Mc > ds2Mc)`
- The test MUST use two **different** `DocumentStore` instances (e.g., `ds1` and `ds2`) that share the same backend, to force a read-after-write consistency check across visibility changes
- The test MUST synchronize on the document ID to prevent interleaved visibility changes from the second store while the first store's visibility change is in progress

### Common pitfalls
- Testing with only a single `DocumentStore` instance — the bug manifests only when reading through a **different** store instance that does not have the updated in-memory state
- Forgetting to synchronize on the document ID (`synchronized (id.intern())`) before asserting `_modCount > previousMc`. Without synchronization, concurrent visibility changes from the second store can interleave and cause `_modCount` to appear not strictly increasing
- Using `assertEquals` instead of a strict greater-than (`>`) comparison — the fix ensures `_modCount` is incremented each time visibility changes, so the test must verify monotonic increase, not equality
- Assuming that a single visibility change increments `_modCount` by exactly 1 — the contract is only that it strictly increases, not by a fixed delta

### Correct test pattern (simplified)
```java
String id = "testDoc";
ds1.createOrUpdateDoc(...); // creates doc with initial _modCount

synchronized (id.intern()) {
    Document doc1 = ds1.getDocument(id);
    long origMc = (Long) doc1.get("_modCount");
    
    ds1.setVisibility(...); // change visibility
    
    Document doc2 = ds2.getDocument(id);
    long ds2Mc = (Long) doc2.get("_modCount");
    assertTrue("_modCount needs to be > " + origMc + " but was " + ds2Mc, ds2Mc > origMc);
    
    // change visibility back
    ds2.setVisibility(...);
    Document doc3 = ds1.getDocument(id);
    long ds1Mc2 = (Long) doc3.get("_modCount");
    assertTrue("_modCount needs to be > " + ds2Mc + " but was " + ds1Mc2, ds1Mc2 > ds2Mc);
}
```

### Incorrect test pattern (would NOT catch this bug)
```java
// Using only one store — buggy code's cached value masks the issue
ds1.createOrUpdateDoc(id, ...);
long mc1 = (Long) ds1.getDocument(id).get("_modCount");
ds1.setVisibility(...);
long mc2 = (Long) ds1.getDocument(id).get("_modCount");
assertTrue(mc2 > mc1); // This would pass even on buggy code because ds1 caches the update
```