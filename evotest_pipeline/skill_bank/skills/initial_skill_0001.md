---
name: branch-merge-conflict-detection-for-changed-properties
description: Teaches how to test that merging branches with conflicting property changes
  correctly throws DocumentStoreException. Use this skill when testing conflict detection
  logic in document-store-based branching systems where two branches independently
  modify the same property.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: EXCEPTION_TEST
---

# branch-merge-conflict-detection-for-changed-properties

## Instructions

# Branch Merge Conflict Detection for Changed Properties

## Instructions

**WHEN** the system under test supports branching (e.g., `mk.branch(rev)`, `mk.merge(branchRev, null)`) and two branches independently modify the **same property** of the **same node** to **different values**:

- **THEN** write a test that:
  1. Creates a base revision with a node containing the property
  2. Creates two branches from the same base revision
  3. On branch 1, commits a change to the property with one value
  4. On branch 2, commits a change to the **same** property with a **different** value
  5. Merges branch 2 **first** (so it succeeds)
  6. Then attempts to merge branch 1 and **expects** `DocumentStoreException` to be thrown
  7. Uses `fail("Must fail with conflict for <testName>")` right after the merge call, with a catch block for `DocumentStoreException`

- **Concrete example** (from `changeChangedPropertyTwoBranches`):
```java
@Test
public void changeChangedPropertyTwoBranches() {
    String rev = mk.commit("/", "+\"foo\":{\"prop\":\"value\"}", null, null);
    
    String branchRev1 = mk.branch(rev);
    branchRev1 = mk.commit("/foo", "^\"prop\":\"bar\"", branchRev1, null);

    String branchRev2 = mk.branch(rev);
    branchRev2 = mk.commit("/foo", "^\"prop\":\"baz\"", branchRev2, null);

    mk.merge(branchRev2, null);

    try {
        mk.merge(branchRev1, null);
        fail("Must fail with conflict for changeChangedProperty");
    } catch (DocumentStoreException e) {
        // expected
    }
}
```

- **Common pitfalls to avoid**:
  1. ❌ Testing the **same value** on both branches — the system may not detect a conflict when the property is changed to the identical value on both branches
  2. ❌ Testing only with `addExistingProperty` or `removeRemovedProperty` scenarios — `changeChangedProperty` (both branches change the same property to different values) is a distinct conflict type that must be tested separately
  3. ❌ Merging the conflicting branch first — you must merge the **non-conflicting** branch first, then verify the **conflicting** branch merge throws
  4. ❌ Testing only single-branch commit/merge patterns without the two-branch scenario — the bug was specifically about **two branches** changing the same property