---
name: merge-with-indexed-parameters-overwrite
description: ''
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# merge-with-indexed-parameters-overwrite

## Instructions

# MergeWith Indexed Parameter Overwrite Bug

## Instructions

- WHEN the TG encounters code that implements a `mergeWith(PageParameters other)` method (or similar merge operation on indexed parameter collections), where indexed parameters from `other` overwrite those in `this` at matching indices, and where non-overlapping indices from `this` should be preserved
- THEN the TG should write a test that creates two `PageParameters` instances where:
  1. `left` has indexed parameters at indices 0 and 1 (e.g., `.set(0, "val0").set(1, "val1")`)
  2. `right` has indexed parameters at indices 1 and 2 (e.g., `.set(1, "val1-r").set(2, "val2")`) — note that index 1 overlaps and index 2 does not exist in `left`
  3. Call `left.mergeWith(right)`
  4. Verify that `left.get(0).toString()` returns `"val0"` (preserved from left since it has no counterpart in right)
  5. Verify that `left.get(1).toString()` returns `"val1-r"` (overwritten by right's value at same index)
  6. Verify that `left.get(2).toString()` returns `"val2"` (added from right's new index)
- The bug occurs when the merge operation incorrectly clears or nullifies indexed parameters from `left` that have no counterpart in `right` at overlapping range boundaries. The test must specifically check `left.get(0)` AFTER the merge — on the buggy version this returns `null` instead of `"val0"`.
- Common pitfall: Only testing that right's parameters are present after merge without also verifying that left's unique parameters (at indices not in right) are preserved. Another pitfall is only testing named parameters during merge and ignoring indexed parameters entirely.
- The failure assertion should be: `assertEquals("val0", left.get(0).toString())` — on the buggy version this will fail with `expected:<val0> but was:<null>`.

### Correct Example
```java
PageParameters left = new PageParameters()
    .add("left", "left", INamedParameters.Type.MANUAL)
    .add("both", "both1", INamedParameters.Type.MANUAL)
    .add("both", "both2", INamedParameters.Type.MANUAL)
    .set(0, "val0")
    .set(1, "val1");
PageParameters right = new PageParameters()
    .add("right", "right", INamedParameters.Type.MANUAL)
    .add("both", "both1-r", INamedParameters.Type.MANUAL)
    .add("both", "both2-r", INamedParameters.Type.MANUAL)
    .set(1, "val1-r")
    .set(2, "val2");
left.mergeWith(right);

// After merge, left.get(0) must still return "val0"
assertEquals("val0", left.get(0).toString());
assertEquals("val1-r", left.get(1).toString());
assertEquals("val2", left.get(2).toString());
assertEquals("left", left.get("left").toString());
assertEquals("right", left.get("right").toString());
assertEquals(2, left.getValues("both").size());
assertEquals("both1-r", left.getValues("both").get(0).toString());
assertEquals("both2-r", left.getValues("both").get(1).toString());
```

### Incorrect Example (would NOT catch the bug)
```java
PageParameters left = new PageParameters().set(0, "val0").set(1, "val1");
PageParameters right = new PageParameters().set(1, "val1-r").set(2, "val2");
left.mergeWith(right);
// Only checking right's values — misses the bug
assertEquals("val1-r", left.get(1).toString());
assertEquals("val2", left.get(2).toString());
// Missing: assertEquals("val0", left.get(0).toString()); — this would fail on buggy version
```