---
name: string-concatenation-within-operator-tostring
description: WHEN overriding toString() on operator expressions (like UnaryOperator)
  that wrap sub-expressions, THEN tests must verify the concatenation produces the
  right parenthesized form. This applies when toString() delegates to child expression
  toString() and uses + concatenation.
code_tags:
- TYPE_HIERARCHY
- CAST_CHECK
- POLYMORPHISM
test_pattern: STATE_TEST
---

# string-concatenation-within-operator-tostring

## Instructions

# String Concatenation Within Operator toString()

## Instructions

- WHEN the TG encounters an expression class (or any class) that overrides `toString()` and builds its output by concatenating the results of child expressions' `toString()` methods using `+` (e.g., `"(" + expression.toString() + ")++"`)
- THEN it should test `toString()` with concrete subclasses/variants of the child expression type, not just a single subtype. Specifically, when the parent expression wraps a polymorphic child expression (such as an `Expression` that can be a `LiteralAccess`, `VariableAccess`, `BinaryOperator`, etc.), the test must exercise at least two different concrete child types to ensure the string concatenation works uniformly.
- The test should verify that `toString()` on the parent expression returns a well-formed string that correctly includes the child expression's string representation, regardless of which concrete subtype the child expression is.
- Use assertions like `assertEquals("(1)++", parent.toString())` and `assertEquals("(x)++", parent.toString())` where one test uses a literal child and another uses a variable access child.
- Common pitfalls: testing `toString()` with only one concrete type of child expression (e.g., only `LiteralAccess`), which might hide a bug where concatenation fails for other subtypes (e.g., `VariableAccess`); assuming `toString()` on the parent class works for all subtypes because it works for one.

### Correct test approach (example)

```java
// Correct: test toString() with at least two different child expression types
UnaryOperator op1 = new UnaryOperator();
op1.setOperand(factory.createLiteral(1));       // LiteralAccess child
assertEquals("(1)++", op1.toString());           // verifies LiteralAccess toString() is included

UnaryOperator op2 = new UnaryOperator();
op2.setOperand(factory.createVariableRead("x")); // VariableAccess child
assertEquals("(x)++", op2.toString());           // verifies VariableAccess toString() is included
```

### Incorrect test approach (example)

```java
// Incorrect: tests only one subtype of child expression
UnaryOperator op = new UnaryOperator();
op.setOperand(factory.createLiteral(1));
assertEquals("(1)++", op.toString());
// No test with VariableAccess or other subtype — misses the bug
```