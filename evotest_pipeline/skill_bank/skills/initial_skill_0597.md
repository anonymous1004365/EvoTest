---
name: clone-cast-conditional-testing
description: When cloning AST nodes with cast expressions, the clone operation must
  properly handle CtConditional elements. Test with combinations of casting and conditional
  expressions to verify no ClassCastException occurs during clone.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# clone-cast-conditional-testing

## Instructions

# Clone Cast Conditional Testing

## Instructions

- WHEN the TG encounters a clone operation on an AST node that involves a cast expression (e.g., `CtCast`/`CastWrite`/`CtConditional`), or any `clone()` method that recursively clones child elements including typed/conditional expressions
- THEN the TG should write a test that:
  1. Creates an AST element that combines casting with conditional logic (e.g., a cast applied to a conditional expression, or a conditional expression whose branches involve casts)
  2. Invokes `clone()` on that element
  3. Verifies that the clone operation completes without throwing a `ClassCastException`
  4. Optionally verifies the cloned element has the correct type/structure after cloning
- The test should specifically target the scenario where a `CtConditional` (ternary expression) is nested inside or combined with a cast expression, because the clone implementation might internally cast child elements to a narrower type that the conditional doesn't match
- Common pitfalls to avoid:
  - ❌ Testing only simple expressions (literals, identifiers) without cast/conditional combinations
  - ❌ Testing the clone of a standalone `CtCast` without a conditional child
  - ❌ Testing the clone of a standalone `CtConditional` without a cast parent
  - ❌ Testing only `String` type parameters when the bug involves `CtTypeReference` or other internal types
  
### Correct Example (catches the bug):
```java
// Create a cast conditional combination
CtConditional<?> conditional = factory.createConditional();
// ... set up conditional with proper types ...
CtCast<?> cast = factory.createCast();
cast.setExpression(conditional);
// Clone should not throw ClassCastException
assertDoesNotThrow(() -> {
    CtCast<?> cloned = cast.clone();
});
```

### Incorrect Example (misses the bug):
```java
// Only testing simple expression clone
CtLiteral<?> literal = factory.createLiteral(42);
// No exception here, but doesn't test the cast-conditional interaction
CtLiteral<?> cloned = literal.clone();
```