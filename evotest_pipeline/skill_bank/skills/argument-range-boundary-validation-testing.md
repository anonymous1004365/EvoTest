---
name: argument-range-boundary-validation-testing
description: 'WHEN a method validates numeric arguments with range constraints (e.g.,
  latitude in [-90,90], longitude in [-180,180]), test that: (1) values exactly at
  the boundary are accepted, (2) values just beyond the boundary (e.g., boundary +
  epsilon) throw IllegalArgumentException, (3) all overloads/delegation paths that
  call the validation are tested, (4) both lower and upper bounds are tested independently.'
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- EXCEPTION_TEST
- NUMERIC_RANGE_VALIDATION
test_pattern: EXCEPTION_TEST
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
  - range validation
  - boundary
  - IllegalArgumentException
  - latitude
  - longitude
  - numeric constraint
  - epsilon
---

WHEN testing numeric argument range validation: 1) Test values exactly at the boundary (e.g., lat=90.0, lat=-90.0) are accepted. 2) Test values just beyond the boundary (e.g., lat=90.0001, lat=-90.0001) throw IllegalArgumentException. 3) Test both lower and upper bounds independently. 4) Test all method overloads that delegate to the validation. 5) Use epsilon values (e.g., 0.0001) just beyond the boundary to trigger the validation. 6) Verify the exception message contains relevant information about the out-of-range parameter.