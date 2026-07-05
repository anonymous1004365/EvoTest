---
name: sliding-window-timestamp-boundary
description: When testing sliding window operators that pre-aggregate (pre-reduce)
  grouped data, verify event timestamps at sliding boundaries are correctly assigned
  to windows, especially for late-arriving events. Use multiple overlapping windows
  with the same timestamp to detect incorrect window reassignment bugs.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- WINDOWING_TIMESTAMP_SLIDING
test_pattern: PARAMETRIC_TEST
---

# sliding-window-timestamp-boundary

## Instructions

# Sliding Window Timestamp Boundary Assignment

## Instructions

- WHEN the TG encounters a **sliding time window operator** (e.g., `SlidingEventTimeWindows`, `SlidingProcessingTimeWindows`) combined with a **pre-reducer** (`ReduceFunction`) that groups elements by key — i.e., a sliding window with pre-aggregation:
  - THEN the TG MUST write a parametric test that sends elements with the **exact same timestamp** that falls at a sliding window boundary (e.g., timestamp = 2 with size=10, slide=4 producing windows [-8,2), [-4,6), [0,10), [4,14), ...  and [2,12), ...) to verify each element is assigned to **exactly the correct set of overlapping windows**.
  - The TG MUST verify that after the pre-reduce step (grouped by key), the output contains the **expected (key, value) pairs per window**, not shifted or misaligned values.
  - **Pitfall to avoid**: Do NOT test with a single window or only test with timestamps that clearly fall in a unique window. The bug manifests when the same timestamp falls on a window boundary, causing the sliding assigner to produce inconsistent window assignments across different invocations or different code paths, especially when combined with pre-reduce state merging.
  - **Example of a correct test**: Create a sliding window of `size=10`, `slide=4`. Send elements with timestamps `1, 2, 3, 4, 5, 6, 7, 8, 9, 10` (keyed). Use a `ReduceFunction` that produces `(timestamp, sum_of_values)` pairs. For timestamp `2`, expect overlapping windows like `[-8,2), [-4,6), [0,10), [4,14)`. After pre-reduce, the element at timestamp `2` should appear in windows that contain `2` — verify that the **first occurrence** in each window's pre-reduced state is correct and that subsequent windows do not mistakenly include a shifted value.
  - **Example of an incorrect test**: Only testing a single element with timestamp far from any boundary, or not keying by element and thus missing the grouped pre-reduce state merge issue.
- WHEN the TG sees a `SlidingTimeGroupedPreReducer` or similar grouped sliding reduce logic:
  - THEN the TG MUST test that when elements with the **same sliding window boundary timestamp** (e.g., `timestamp=2` for windows starting at `-8, -4, 0, 4...`) are processed, each element's **value is correctly pre-reduced into the correct window's state**, and that on window firing, the output reflects the correct value — not a value from a different window's pre-reduce state.
  - **Pitfall**: The bug occurs because after merging or updating pre-reduce state for a boundary timestamp, the state key mapping can become inconsistent — a subsequent window may produce the pre-reduced value from an earlier window for keys that share the same boundary timestamp.
- WHEN writing assertions for sliding window pre-reduce output:
  - THEN the TG MUST verify the **exact (key, value) tuples per window**, not just the count or presence of elements. Use expected sequences like `[(key1, value1), (key2, value2)]` for each window.
  - **Pitfall**: Just checking that all expected windows fire (e.g., checking window count) does NOT catch this bug. The bug changes **which values** appear in which window, not whether values appear at all.
- Common pitfalls summary:
  1. Testing only with timestamps that are unique to a single window — the bug requires boundary timestamps shared by multiple overlapping windows.
  2. Testing without pre-reduce aggregation — the bug manifests only when a `ReduceFunction` is combined with the sliding assigner.
  3. Testing without keying by element — the bug is in the grouped pre-reduce state, so tests must use `keyBy()`.
  4. Verifying only that the total number of output records matches expectations — the wrong values can be in the right windows.