---
name: stack-underflow-precondition-validation
description: WHEN a method pops elements from a stack or collection without first
  checking that the collection has enough elements, THEN generate tests that provide
  inputs causing the collection to be underfilled when an operation is attempted,
  and verify that the correct exception type (e.g., IllegalArgumentException) is thrown
  rather than EmptyStackException or ArrayIndexOutOfBoundsException.
code_tags:
- STACK_UNDERFLOW
- PRECONDITION_CHECK
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- DATA_STRUCTURE_OPERATION
test_pattern: EXCEPTION_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - PASS_FAIL
  transition_tags:
  - STACK_UNDERFLOW
  - PRECONDITION_CHECK
  keywords:
  - stack
  - pop
  - underflow
  - empty stack
  - size check
  - precondition
  - postfix
  - evaluation
---

WHEN the TG encounters a method that pops elements from a stack or deque (e.g., Stack.pop(), Deque.removeFirst()) inside a loop or conditional branch, THEN: 1) Identify whether there is a precondition check (if (size < required) throw ...) before the pop operations. 2) If the check exists in the fixed version, generate tests that exercise the check by providing inputs that would cause underflow (e.g., a single operator token in a postfix expression evaluator). 3) Verify that the buggy version throws the wrong exception type (e.g., EmptyStackException) while the fixed version throws the correct one (e.g., IllegalArgumentException). 4) Cover all operators/branches that could trigger the underflow, not just one.