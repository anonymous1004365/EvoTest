---
name: nested-form-onerror-ordering
description: When testing form validation error callbacks in component hierarchies
  with nested forms, the TG should verify that onError is called on the outermost
  submitted form first, then propagates inward. This prevents order-dependent bugs
  where error handling follows incorrect traversal.
code_tags:
- ORDER_DEPENDENCY
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# nested-form-onerror-ordering

## Instructions

# Nested Form OnError Propagation Ordering

## Instructions

**WHEN** the TG encounters code that processes form validation errors (`onError()`, `delegateSubmit()`, or error handling) in a hierarchy where `Form` components contain other `Form` components (nested forms):

- **THEN** the TG should verify the *order* in which `onError()` is invoked across nested forms when validation fails, not just that it is invoked.

- **WHEN** a form with validation errors contains nested child forms, and the outer form is submitted:
  - **THEN** the test should verify that `onError()` is called on the **outermost/ancestor form first**, before being called on inner/nested forms. Do NOT assume traversal starts from the innermost (deepest) form.
  - **CONCRETE EXAMPLE**: Given a form hierarchy `outerForm > middleForm > innerForm`, when a field inside `innerForm` has a validation error and the user submits `outerForm`, the expected `onError()` invocation order is `[outerForm, middleForm, innerForm]` (outermost-first), NOT `[innerForm, middleForm, outerForm]` (innermost-first).

- **WHEN** writing a test for nested form error propagation:
  - **THEN** create a page with at least 3 levels of form nesting (outer → middle → inner).
  - **THEN** add a `TextField` to the innermost form's component hierarchy.
  - **THEN** submit the outermost form (e.g., via `tester.newFormTester("outerForm").submit()`).
  - **THEN** trigger a validation error (e.g., by providing invalid input to the inner field).
  - **THEN** capture the order of `onError()` calls (e.g., by having each form log its ID to a `List<String>`).
  - **THEN** assert the list equals `[outerFormId, middleFormId, innerFormId]`.

- **COMMON PITFALLS**:
  - ❌ Testing only with a single form (no nesting) — this misses the ordering bug entirely.
  - ❌ Testing with only 2 levels of nesting — the bug may only manifest with 3+ levels.
  - ❌ Asserting only that `onError()` is called, without checking the sequence of calls.
  - ❌ Assuming the error propagates from the component that failed validation (innermost-first), instead of from the submitted form (outermost-first).

- **CORRECT EXAMPLE** (Java-like pseudocode):
  ```java
  // Page with: outerForm > middleForm > innerForm
  // innerForm has a TextField that fails validation
  List<String> errorOrder = new ArrayList<>();
  
  outerForm.onError = () -> errorOrder.add("outerForm");
  middleForm.onError = () -> errorOrder.add("middleForm");
  innerForm.onError = () -> errorOrder.add("innerForm");
  
  tester.newFormTester("outerForm").submit();
  
  // Verify outermost-first ordering
  assertEquals(
      List.of("outerForm", "middleForm", "innerForm"),
      errorOrder
  );
  ```

- **INCORRECT EXAMPLE**:
  ```java
  // ❌ Only checks that onError was called, not the order
  assertTrue(errorOrder.contains("outerForm"));
  assertTrue(errorOrder.contains("innerForm"));
  
  // ❌ Assumes innermost-first order
  assertEquals(
      List.of("innerForm", "middleForm", "outerForm"),
      errorOrder
  );
  ```