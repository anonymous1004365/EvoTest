---
name: merge-sorted-iterators-invariant
description: When merging multiple sorted iterators (e.g., from getPreviousDocs),
  ensure the merge algorithm enforces that emitted keys/values respect the total sort
  order. Test with interleaved values across iterators where later iterators have
  smaller keys than earlier ones to catch missing ordering invariants.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# merge-sorted-iterators-invariant

## Instructions

# Merge-Sorted Iterators Invariant Violation

## Instructions

- WHEN a method merges values from multiple sorted iterators (e.g., `getPreviousDocs()` → `getValueMap()`) into a single sorted result
- THEN the test MUST construct a scenario where **two or more iterators contain interleaved values whose global ordering is NOT monotonic** — specifically, the test should have values in iterator A that are **larger** than values in iterator B, but with B having a value that is **smaller** than A's last value. This forces the merge algorithm to compare values across iterators and detect if it fails to enforce the total order invariant.
- For example, when merging `_revisions` entries from a current document and its previous documents (`getPreviousDocs`), provide:
  - Iterator 1 (current doc): revisions with keys `r1`, `r2`, `r3` (sorted ascending)
  - Iterator 2 (previous doc 1): revisions with keys `r1'`, `r2'`, `r3'` where `r1' < r3` but `r2' > r3` (i.e., interleaved)
  - Verify the merged output is strictly sorted: each consecutive pair satisfies `previous < next`
- On the **buggy** implementation, the merge produces non-monotonic results (e.g., `r3` then `r1'`) — the test MUST assert an `IllegalStateException` or detect the misordered pair
- **Common pitfalls to avoid:**
  - Testing with only non-overlapping iterators (e.g., A: [1,2,3], B: [4,5,6]) — this passes on buggy code because no cross-iterator comparison is ever needed
  - Testing with a single iterator — the bug only manifests when merging multiple iterators
  - Using only equal-length iterators — the bug can appear with varying lengths
  - Assuming the merge algorithm correctly compares a "current" entry against a "next" entry without checking that the next is actually from a different iterator after the previous was consumed
  
- **Correct test approach (catches the bug):** Feed three `SortedMap` iterators (or simulate `Iterable<NodeDocument>`) where the second iterator has a value smaller than the first iterator's last value, forcing the merge to re-order. Assert that each successive key is strictly greater than the previous one, or catch an `IllegalStateException` from a broken invariant check.

- **Wrong test approach (misses the bug):** Provide iterators with values that are already globally sorted (e.g., A: [1,3], B: [2,4]) — this works by accident even on buggy code because the merge happens to pick values in ascending order without needing to backtrack.