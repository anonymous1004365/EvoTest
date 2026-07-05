---
name: field-access-target-type-validation
description: When setting a CtExpression target on a field access that previously
  had a CtTypeReference target (type-level), the type must be properly validated.
  Use this skill when calling setTarget() on field accesses where the target switches
  between type and instance references.
code_tags:
- EXPRESSION_TARGET_SETTING
test_pattern: STATE_TEST
---

# field-access-target-type-validation

## Instructions

# Field Access Target Type Validation

## Instructions

- WHEN the TG encounters code that calls `setTarget(CtTypeReference)` on a `CtFieldAccess` or similar AST element, and later calls `setTarget(CtExpression)` (especially a `CtLiteral` or any non-type-reference expression)
- THEN it should write a test that:
  1. Creates a `CtFieldAccess` whose target is initially a `CtTypeReference` (type-level static access)
  2. Calls `setTarget()` with a different type of expression (e.g., a string `CtLiteral` or other `CtExpression`)
  3. Verifies that the field access repackages its target correctly, with particular attention to the type information — the field access's `getType()` should NOT throw an exception
  4. Expects that on the **buggy** version, calling a method like `getType()` on the field access (or looping over its target's metadata) throws a `ClassNotFoundException`, `NullPointerException`, or `AssertionError`
  5. Expects that on the **fixed** version, the operation succeeds without exception

- **Mistakes to avoid**:
  - DO NOT write tests that only set one type of target and read it back — the bug manifests specifically when the target *changes* from a `CtTypeReference` to a different expression type (e.g., a `CtLiteral`)
  - DO NOT assume the target repackaging is correct just because the setter returns successfully — you must exercise the target's type-related methods (e.g., `getType()`, `getActualClass()`) to trigger the bug
  - DO NOT forget to use the actual types from the codebase: the concrete field access implementation, the concrete target expression types (`CtTypeReference`, `CtLiteral`), and the expected failure mode (`ClassNotFoundException`, `AssertionError`)

- **Correct example** (fixed version should pass, buggy version should throw):
  ```java
  // Create a field access with a CtTypeReference as target
  CtFieldAccess fieldAccess = factory.createFieldAccess();
  CtTypeReference<?> typeRef = factory.Type().createReference(String.class);
  fieldAccess.setTarget(typeRef);
  
  // Switch target to a different expression type (e.g., a literal)
  CtLiteral<String> literal = factory.createLiteral("someValue");
  fieldAccess.setTarget(literal);
  
  // Trigger the repackaging bug by calling getType()
  // Buggy version throws ClassNotFoundException/AssertionError here
  fieldAccess.getType();
  ```

- **Incorrect example** (does not trigger the bug):
  ```java
  // Only sets one target type — no transition, so bug won't manifest
  CtFieldAccess fieldAccess = factory.createFieldAccess();
  CtLiteral<String> literal = factory.createLiteral("test");
  fieldAccess.setTarget(literal);
  assertEquals("test", ((CtLiteral)fieldAccess.getTarget()).getValue());
  ```