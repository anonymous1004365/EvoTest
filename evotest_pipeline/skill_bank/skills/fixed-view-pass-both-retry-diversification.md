---
name: fixed-view-pass-both-retry-diversification
description: WHEN a generated retry suite passes on both fixed and buggy versions,
  use only fixed-version evidence to try a different behavior class instead of varying
  the same happy path.
code_tags:
- PASS_BOTH_RECOVERY_FIXED_VIEW
- HYPOTHESIS_DIVERSIFICATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
retrieval:
  applicable_tiers:
  - PASS_BOTH
  keywords:
  - pass_both
  - retry
  - diversify
  - boundary
  - parser
  - state
  - oracle
---

# Fixed-view PASS_BOTH retry diversification

When a fixed-valid generated suite still passes both versions, do not keep
testing the same happy path with small constant variations. Use only the fixed
checkout and previous generated-test feedback to form a different hypothesis.

Prefer a new behavior class such as:

- boundary state: empty/singleton/full/wrap-around/overflow/underflow;
- parser or scanner loop boundary: delimiter at start/end, missing delimiter,
  nested delimiter, duplicate attributes, unmatched closing token;
- nested or recursive structure: parent/child order, clone/deep-copy aliasing,
  mutation after copy;
- ordering and comparison: equal keys, duplicate values, inclusive/exclusive
  range endpoints, stable ordering;
- encoding and binary layout: BOM, non-zero buffer offset, charset conflict,
  endian mismatch, field-width boundary;
- API contract error path: invalid input that fixed code handles by documented
  exception or fallback.

For each retry, derive the oracle from fixed-version public behavior or from
documented API contracts. Do not rely on git diffs, triggering tests, buggy
version behavior, actual changed methods, or patch information.
