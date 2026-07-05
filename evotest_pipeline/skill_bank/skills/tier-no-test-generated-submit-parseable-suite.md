---
name: tier-no-test-generated-submit-parseable-suite
description: WHEN the agent has spent more than 20 tool-call steps analyzing source
  code without producing any test methods, AND the final tier is NO_TEST_GENERATED,
  THEN the agent should stop exploring and convert its current understanding into
  a small valid test class. Preserve the test class name, package, and 2-4 self-contained
  tests that exercise the most basic decoding paths.
code_tags:
- TIER_RECOVERY
- NO_TEST_GENERATED
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - NO_TEST_GENERATED
  transition_tags: []
  keywords:
  - no_test_generated
  - decode
  - analysis_loop
  - stuck
  - no test methods
---

WHEN the agent has spent more than 20 tool-call steps analyzing source code without producing any test methods, AND the final tier is NO_TEST_GENERATED, THEN the agent should stop exploring and convert its current understanding into a small valid test class. Preserve the test class name, package, and 2-4 self-contained tests that exercise the most basic decoding paths.