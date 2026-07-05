---
name: xrange-processor-comparison-operator-testing
description: WHEN a version range parser processes X-ranges (wildcard ranges like
  '2.x', '2.*', or just '2') combined with comparison operators (>, >=, <, <=), test
  that the parser correctly expands the range. The common bug is that 'minor = 0'
  is set unconditionally before the GT/LTE branching logic, causing 'isX(minor)' to
  return false prematurely.
code_tags:
- VERSION_RANGE_COMPARISON
- VERSION_RANGE_PARSING
- BOUNDARY_CHECK
- COMPARISON_OPERATOR_BUG
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_FAIL
  - BUG_DETECTED
  transition_tags: []
  keywords:
  - semver
  - xrange
  - XRangeProcessor
  - version range
  - comparison operator
  - wildcard
  - satisfies
---

WHEN testing X-range processing with comparison operators: 1) Test '>2' should expand to '>=3.0.0' (not '>=2.1.0'). 2) Test '<=2' should expand to '<3.0.0' (not '<2.1.0'). 3) Test '>=2' should expand to '>=2.0.0'. 4) Test '<2' should expand to '<2.0.0'. 5) Use discriminating versions like 2.5.0, 2.1.0, 3.0.0, 2.0.0 to distinguish buggy from correct behavior. 6) Test with versions that fall in the gap between buggy and correct expansions.