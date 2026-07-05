---
name: empty-block-state-mutation
description: When adding empty blocks to AST structures like CtBlock, the implicit
  constructor or body state may not be properly set. This skill teaches how to test
  adding an empty block and verifying the implicit state is correctly initialized.
code_tags:
- NULL_CHECK
- VALIDATION
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# empty-block-state-mutation

## Instructions

# Empty Block State Mutation

## Instructions

- WHEN the test involves creating an empty `CtBlock` and adding it to a model element (e.g., a class or constructor), THEN verify the internal state of the added block is consistent — specifically, the `implicit` flag or similar boolean state should be `false` for user-added blocks, not incorrectly inherited as `true`.

- WHEN testing `addStatement` or similar block mutation operations, THEN after adding a new empty `CtBlock`, verify that the block's implicit/empty state is correctly reset and that `isImplicit` returns `false`.

- WHEN a factory method like `createClass()` or `createConstructor()` creates implicit bodies, and you want to add explicit empty blocks, THEN ensure you test that adding blocks afterward does not retain implicit state from the constructor's initial implicit block.

- Common pitfalls:
  - Testing only with non-empty statements instead of empty blocks — empty blocks are the edge case.
  - Assuming that an empty block created by the factory (e.g., `CtBlockImpl()`) already has the correct implicit flag — it may inherit `true` from an implicit constructor body.
  - Failing to call a setter to reset `implicit` to `false` after the block is added to a parent that had an implicit body.

## Examples

### Correct approach:
```java
// Create a class (which has an implicit constructor body)
CtClass<?> cls = factory.createClass("MyClass");
// Add an empty block as a statement
CtBlock<?> emptyBlock = factory.createBlock();
cls.addStatement(emptyBlock);
// Verify the empty block is NOT implicit
assertFalse("Empty block added to class should not be implicit", block.isImplicit());
```

### Incorrect approach:
```java
// Creating a class and testing only non-empty additions
CtClass<?> cls = factory.createClass("MyClass");
cls.addStatement(factory.createCodeSnippetExpression("int x = 1"));
// This never catches the implicit state bug on empty blocks
```