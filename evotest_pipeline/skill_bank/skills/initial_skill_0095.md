---
name: repeated-rebase-idempotency
description: ''
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- IDEMPOTENT_CONSUMER
test_pattern: STATE_TEST
---

# repeated-rebase-idempotency

## Instructions

# Repeated Rebase Idempotency

## Instructions

- WHEN the TG encounters a `rebase(branchRevision, headRevision)` or similar method that merges trunk changes into a branch
- THEN the TG should write a test that calls `rebase()` TWICE with the same arguments (same branch revision, same head revision or null for latest head) and asserts that both calls return the **exact same branch revision string** (i.e., `assertEquals(firstResult, secondResult)`).
- WHEN the TG tests a rebase operation that returns a new branch revision string, it MUST verify that calling `rebase()` again with the returned branch revision and the same head produces the **same** revision string (idempotent), not a different one like `br...-b-1` vs `br...-c-1`.
- The test must also verify the content after both rebase calls is consistent — for example, nodes and properties added on the trunk are visible via the rebased branch.
- Common pitfalls:
  - ❌ Testing `rebase()` only once and assuming it is correct. The bug only manifests on the SECOND rebase call with the same head.
  - ❌ Asserting only content correctness post-rebase without checking that the returned revision string is identical between repeated calls.
  - ❌ Using different head revisions for the two rebase calls (which would legitimately produce different results).
  - ✅ Correct approach: create a branch, make changes on trunk, call `rebase(branch, null)` and save the result as `rebased1`, then call `rebase(rebased1, null)` again and assert `assertEquals(rebased1, rebased2)`.

### Example (correct)

```java
@Test
public void rebaseMultiple() {
    String branch = mk.branch(null);
    mk.commit("", "+\"/a\":{}", null, null); // trunk change
    
    String rebased1 = mk.rebase(branch, null);
    String rebased2 = mk.rebase(rebased1, null);
    
    // The fix: repeated rebase with same head must not create new branch revision
    assertEquals("Repeated rebase must return same revision", rebased1, rebased2);
    
    // Content must still be correct via both revisions
    JSONObject json = parseJSONObject(mk.getNodes("/", rebased2, 0, 0, -1, null));
    assertNotNull(json.get("a"));
}
```

### Example (incorrect — missing idempotency check)

```java
@Test
public void rebaseMultiple() {
    String branch = mk.branch(null);
    mk.commit("", "+\"/a\":{}", null, null);
    String rebased = mk.rebase(branch, null);
    
    // ❌ Only checks content, doesn't verify that a second rebase returns the same revision
    JSONObject json = parseJSONObject(mk.getNodes("/", rebased, 0, 0, -1, null));
    assertNotNull(json.get("a"));
}
```