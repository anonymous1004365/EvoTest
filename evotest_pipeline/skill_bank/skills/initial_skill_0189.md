---
name: fully-qualified-field-access-simplification
description: When accessing fields where the variable type uses fully qualified names
  (e.g., `org.Foo` instead of `Foo`), the compiler may incorrectly simplify or fail
  to qualify field references, especially in try-catch blocks or complex scopes. Apply
  this skill to verify that fully qualified field access is preserved under such conditions.
code_tags:
- STATE_MUTATION
- EDGE_CASE_INPUT
- VALIDATION
- TYPE_CONVERSION
- CONDITIONAL_BRANCH
test_pattern: STATE_TEST
---

# fully-qualified-field-access-simplification

## Instructions

# Fully Qualified Field Access Simplification

## Instructions

- WHEN the TG encounters code that constructs or accesses a field of a type using a fully qualified class name (e.g., `org.example.MyClass.STATIC_FIELD`), and that access occurs inside a try-catch block or other scoped context
- THEN the TG should write a test that:
  1. Creates a code snippet where a field is accessed via its fully qualified class name inside a try-catch or similar block
  2. Builds and processes the code with the Spoon model builder
  3. Asserts that the field access in the resulting AST or output source code retains the fully qualified form (i.e., the type name is not stripped to its simple name)
  4. Specifically, verifies that the `TargetedExpression` or field access node's target type remains qualified (not simplified to just the simple class name)
- Common pitfalls to avoid:
  - Testing only simple field access expressions (e.g., `MyClass.FIELD`) instead of fully qualified ones (e.g., `com.example.MyClass.FIELD`)
  - Testing field access outside of try-catch or complex scoping constructs, where the bug may not manifest
  - Using only string-based comparisons without also checking the AST model structure (e.g., the `TargetedExpression`'s target)

### Correct Example (test that would catch this bug)

```java
@Test
public void testNoFQNWhenUsedInTryCatch() {
    // code: a try-catch block with a fully qualified static field access
    String code = "class A {\n" +
                  "  void m() {\n" +
                  "    try {\n" +
                  "      System.out.println(java.util.Collections.EMPTY_LIST);\n" +
                  "    } catch(Exception e) {}\n" +
                  "  }\n" +
                  "}";
    Launcher launcher = new Launcher();
    launcher.addInputResource(new StringInputResource(code));
    launcher.buildModel();
    CtClass<?> cls = launcher.getFactory().Type().get("A");
    // Assert that the field access in the AST keeps the fully qualified target
    CtInvocation<?> invocation = cls.getMethodsByName("m").get(0).getBody().getStatement(0);
    // ... further assertions on the field access target not being simplified
}
```

### Incorrect Example (would NOT catch this bug)

```java
@Test
public void testSimpleFieldAccess() {
    // Only tests simple (non-fully-qualified) field access outside try-catch
    String code = "class A { void m() { System.out.println(Collections.EMPTY_LIST); } }";
    Launcher launcher = new Launcher();
    launcher.addInputResource(new StringInputResource(code));
    launcher.buildModel();
    // This test does not exercise the bug because:
    // 1. The field access is not fully qualified (no package prefix)
    // 2. It is not inside a try-catch block
}
```