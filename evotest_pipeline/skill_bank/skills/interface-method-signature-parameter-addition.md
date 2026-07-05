---
name: interface-method-signature-parameter-addition
description: 'WHEN an interface default method or abstract method has a parameter
  added (signature change), test that: (1) the new parameter is correctly passed through
  from the calling context, (2) implementations that use the new parameter for conditional
  logic produce correct output, and (3) the old behavior (without the parameter) would
  fail or produce incorrect results.'
code_tags:
- INTERFACE_METHOD_SIGNATURE_CHANGE
- PARAMETER_ADDITION
- ARGUMENT_VALIDATION
- OUTPUT_FORMATTING
test_pattern: STATE_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - PASS_FAIL
  transition_tags: []
  keywords:
  - interface
  - method signature
  - parameter added
  - default method
  - signature change
  - provideCoordinates
---

WHEN the TG encounters an interface whose method signature has changed (e.g., a parameter was added): 1) Identify which implementations use the new parameter for conditional logic. 2) Test those implementations with different values of the new parameter to verify correct conditional behavior. 3) Test that the calling method correctly passes the new parameter through. 4) If possible, verify that the buggy version (without the parameter) would produce incorrect output. 5) Do not only test implementations that ignore the new parameter.