---
name: ternary-parenthesis-pretty-printing
description: When a code transformation or pretty printer handles ternary expressions
  nested in blocks, the TG should test that parentheses are correctly added around
  ternary expressions assigned to local variables, not just in return statements or
  boolean contexts. This prevents the bug where a ternary expression on a local variable
  assignment loses its required parentheses in the output.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# ternary-parenthesis-pretty-printing

## Instructions

# Ternary Parenthesis Pretty Printing

## Instructions

- WHEN the TG encounters a pretty printer or code generator that processes ternary expressions (`? :`) within assignment contexts (e.g., `int x = a ? b : c;`)
- THEN the TG should test that the output retains **mandatory parentheses** around the ternary expression when it is assigned to a local variable, as the ternary operator has lower precedence than assignment in some languages, and the pretty printer may incorrectly omit them
- Specifically, include a test where a ternary expression is used as the right-hand side of a local variable declaration inside a block (e.g., a method body), and verify the printed/transformed string contains parentheses: e.g., `int x = (a ? b : c);`
- The test should use a **source input** that explicitly has parentheses around the ternary (e.g., `int x = (condition ? value1 : value2);`), then transform it through the printer, and assert the output **still contains the parentheses**
- Common pitfalls to avoid:
  - Testing only ternary expressions in return statements or boolean conditions — these may work without parentheses due to context, masking the bug
  - Forgetting to test with local variable assignments **inside a method body or block** where the expression type is concrete (not just abstract syntax tree manipulation)
  - Using only one type of ternary operand (e.g., only `String` or only `int`) — test with both to ensure type doesn't mask the issue
  - Testing only that the code compiles, rather than directly asserting the string output matches the expected formatted source

**Correct example** (catches the bug):
```java
@Test
public void testTernaryParenthesesOnLocalVariable() {
    String code = "class Foo { void bar() { int x = (true ? 1 : 0); } }";
    CtClass<?> ctClass = launcher.parseClass(code);
    String result = ctClass.prettyprint();
    assertTrue("Ternary parentheses should be preserved", 
               result.contains("(true ? 1 : 0)"));
}
```

**Incorrect example** (wrong format - masks the bug):
```java
@Test
public void testTernary() {
    // Only testing compilation, not the formatted output string
    String code = "class Foo { void bar() { return true ? 1 : 0; } }";
    CtClass<?> ctClass = launcher.parseClass(code);
    // This would pass even on the buggy version because return context is different
    assertDoesNotThrow(() -> ctClass.prettyprint());
}
```