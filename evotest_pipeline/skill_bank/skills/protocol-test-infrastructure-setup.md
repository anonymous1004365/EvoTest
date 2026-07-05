---
name: protocol-test-infrastructure-setup
description: WHEN generating tests for a protocol decoder in a project that uses a
  custom test base class (e.g., ProtocolTest extending BaseTest), THEN the TG MUST
  first inspect the existing test class to identify the base class and helper methods
  available. The generated test class must extend the same base class and use the
  same helper methods (inject, binary, verifyNull, verifyAttribute, verifyPositions)
  to ensure the test compiles and runs correctly.
code_tags:
- TEST_INFRASTRUCTURE
- PROTOCOL_TEST_BASE_CLASS
- TEST_SETUP
- MOCK_BEHAVIOR
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - FAIL_ON_FIXED
  - FAIL_ON_BUGGY
  - COMPILE_FAIL
  transition_tags:
  - COMPILATION_ERROR
  - TEST_SETUP_FAILURE
  keywords:
  - ProtocolTest
  - BaseTest
  - inject
  - binary
  - verifyNull
  - verifyAttribute
  - verifyPositions
  - test base class
  - mock behavior
  - device session
---

WHEN the TG encounters a protocol decoder test class that extends a custom base class (e.g., ProtocolTest), THEN: (1) Read the existing test class to identify the base class and available helper methods. (2) Ensure the generated test class extends the same base class. (3) Use the same helper methods (inject, binary, verifyNull, verifyAttribute, verifyPositions) for test setup and assertions. (4) Verify that binary hex data strings are complete and correctly formatted by cross-referencing with working test data from the host test class. (5) Check that the test class is in the correct package with proper imports. (6) Understand the mock behavior: inject() creates a new mock each call, so tests needing a device session must call a login message first.