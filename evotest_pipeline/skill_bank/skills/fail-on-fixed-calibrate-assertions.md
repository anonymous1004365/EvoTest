---
name: fail-on-fixed-calibrate-assertions
description: WHEN a generated suite fails on the fixed version (FAIL_ON_FIXED), the
  assertions are too strong or the setup violates the fixed API contract. Re-read
  fixed source and existing tests, reduce the assertions to fixed-valid behavior,
  and remove scenarios unsupported by the fixed code.
code_tags:
- TIER_RECOVERY
- FAIL_ON_FIXED
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  transition_tags: []
  keywords:
  - fail_on_fixed
  - calibrate
  - fixed behavior
  - assertion too strong
  - repair
---

WHEN a generated suite fails on the fixed version, the TG should: (1) Re-read the fixed version's source code for the focal method, (2) Examine existing test files for patterns showing how the API is actually used, (3) Remove or correct assertions that assume behavior not present in the fixed version, (4) For connect/factory methods, distinguish between connect-time validation (syntax) and execution-time validation (protocol support), (5) For DOM structure, verify the actual child order (e.g., <head> before <body>).