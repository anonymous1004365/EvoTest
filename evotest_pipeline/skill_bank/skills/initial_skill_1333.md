---
name: fully-qualified-name-shadowed-by-local-variable
description: When code resolves fully qualified names (FQNs) in inner classes that
  shadow outer fields with local variables, the FQN may be wrongly replaced with a
  simple name. Use this skill to test FQN resolution when local variable names conflict
  with field or type names in inner class contexts.
code_tags:
- FULLY_QUALIFIED_NAME_RESOLUTION
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# fully-qualified-name-shadowed-by-local-variable

## Instructions

# Fully Qualified Name Resolution With Local Variable Shadowing

## Instructions

- WHEN the TG encounters code that resolves whether field accesses in inner classes should use fully qualified names (FQNs) instead of simple names, AND the resolution logic must consider whether a local variable in an enclosing scope shadows the accessed field/type name
- THEN the TG should write a STATE_TEST that:
  1. Creates a test input (source code) where an inner class references a field from an outer class, AND a local variable in an enclosing scope has the same name as a field being accessed
  2. Constructs a case where the accessed target (e.g., `String`) is accessed via its FQN (e.g., `java.lang.String`) inside an inner class that is itself inside a method containing a local variable that shadows the simple name `String`
  3. Verifies that after processing (e.g., pretty-printing, auto-import resolution), the reference remains a fully qualified name (e.g., `java.lang.String`) and is NOT incorrectly shortened to the simple name (e.g., `String`)
  4. Asserts that the output/reconstructed code retains the FQN form, confirming that the presence of the local variable shadowing did not cause incorrect short-name substitution

- Common pitfalls to avoid:
  - Testing only with type-level name conflicts (e.g., inner class fields vs outer class fields) without also testing method-local variable shadowing
  - Assuming that FQN resolution only depends on imported types; forgetting that local variable names in enclosing methods can also trigger false positive "already defined" collisions
  - Only testing one element type (e.g., only `String`); the TG should test with multiple types (e.g., `java.lang.String`, `java.util.List`) to confirm the behavior is general
  - Not covering the case where the local variable name matches the simple name of a type used in a field access expression (e.g., `String foo` shadows the class name `String`)

- Example correct test (pseudocode):

  ```java
  // Source code input:
  // class A {
  //     String field = "hello";
  //     void method() {
  //         String String = "shadow";  // local variable shadows java.lang.String
  //         class Inner {
  //             void innerMethod() {
  //                 String s = java.lang.String.valueOf(123);
  //             }
  //         }
  //     }
  // }
  //
  // After processing, verify that "java.lang.String.valueOf" is NOT shortened to "String.valueOf"
  // since String is already a local variable name and cannot be used as a type reference.
  String result = processor.prettyprint(input);
  assertTrue(result.contains("java.lang.String.valueOf"));
  assertFalse(result.contains("String.valueOf(123)"));
  ```

- Example incorrect test (pitfall):

  ```java
  // INCORRECT: Only tests outer/inner field shadowing without local variable shadowing
  // class A {
  //     String field;
  //     class Inner {
  //         int field;  // shadows outer field, but different type - no FQN issue here
  //         void m() { System.out.println(field); }
  //     }
  // }
  // This misses the bug entirely because the bug only triggers when a LOCAL VARIABLE
  // (not just an inner class field) shadows a name used in FQN resolution.
  ```