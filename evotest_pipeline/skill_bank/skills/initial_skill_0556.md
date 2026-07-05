---
name: variable-access-check-null
description: When testing code that handles variable access or local variable declarations,
  the TG should verify that the code correctly handles multiple declarations of the
  same local variable name without throwing NullPointerException.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# variable-access-check-null

## Instructions

# Variable Access Handling with Multiple Local Variable Declarations

## Instructions

- WHEN the TG encounters code that accesses local variables or processes variable declarations (e.g., `CtVariableAccess`, `CtLocalVariable`)
- THEN it should test with multiple declarations of the same local variable name in the same scope, and verify that no `NullPointerException` is thrown
- Include a test case that declares a local variable, then declares another local variable with the same name in the same block (e.g., `int x = 1; int x = 2;`), and tries to access or resolve the variable reference
- The test should verify that the code handles this edge case gracefully (e.g., by returning the first declaration, or by handling the ambiguity without crashing)
- Common pitfalls: testing only single declarations of local variables, not testing re-declaration of the same variable name, assuming variable names are unique within a scope
- Correct example: create a test method that builds a model with two local variables sharing the same name, then calls the method under test (e.g., `getVariableDeclaration`) and asserts no exception is thrown
- Incorrect example: testing only with unique variable names, or testing only with field/parameter accesses and ignoring local variable re-declarations