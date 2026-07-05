---
name: shared-mutable-default-defensive-copy
description: WHEN a class has a static final Set/Collection/Map constant used as the
  default value for an instance field, AND mutation methods (addAll, removeAll, putAll,
  etc.) are called on that field without first checking if it references the shared
  constant, THEN test that mutating one instance's collection does not affect other
  instances that use the default.
code_tags:
- DEFENSIVE_COPY
- SHARED_MUTABLE_STATE
- SIDE_EFFECT_FREE
- STATE_MUTATION
- COPY_ON_WRITE
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - FAIL_FIXED
  transition_tags:
  - SHARED_MUTABLE_DEFAULT
  - DEFENSIVE_COPY
  - COPY_ON_WRITE
  keywords:
  - shared mutable default
  - defensive copy
  - copyOnWrite
  - statelessness
  - side effect
  - mutation
---

WHEN a class has a static final Set/Collection/Map constant used as the default value for an instance field, AND mutation methods (addAll, removeAll, putAll, etc.) are called on that field without first checking if it references the shared constant, THEN the TG should test that mutating one instance's collection does not affect other instances that use the default. The test should: (1) create instance A and call a mutation method, (2) create instance B (using default), (3) verify instance B's behavior is unaffected by A's mutation. This catches the missing-defensive-copy bug.