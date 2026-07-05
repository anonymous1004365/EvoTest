---
name: comparison-operator-bug-in-stack-algorithm
description: WHEN a monotonic-stack algorithm uses a comparison operator (<= or <)
  to decide whether to pop elements from the stack, THEN test with consecutive equal
  values to discriminate between `<=` (pop on equal) and `<` (keep on equal). The
  bug is typically that `<=` is used when `<` is correct, causing incorrect span/distance
  calculations for equal values.
code_tags:
- COMPARISON_OPERATOR_BUG
- STACK_ALGORITHM
- MONOTONIC_STACK
- BOUNDARY_CHECK
- EDGE_CASE_INPUT
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - PASS_BOTH
  transition_tags: []
  keywords:
  - calculateSpans
  - stock span
  - monotonic stack
  - comparison operator
  - equal prices
  - OnlineStockSpan
  - <= vs <
  - stack pop condition
---

WHEN the focal method uses a Stack and a while-loop condition like `prices[stack.peek()] <= prices[i]` (or `<`) to pop indices, THEN: 1) Identify whether the correct operator should be `<` or `<=` based on the problem definition. 2) Write tests with consecutive equal values (e.g., {5,5,5}, {10,5,5}) where the expected output differs between `<=` and `<`. 3) Verify the test passes on the fixed version and fails on the buggy version. 4) Also test strictly increasing, strictly decreasing, and mixed sequences.