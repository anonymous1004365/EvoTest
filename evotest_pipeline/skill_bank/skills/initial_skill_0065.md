---
name: default-constructor-is-empty-body
description: When a test validates that generated default constructors are properly
  recognized as having an empty body (no explicit statements), the test should verify
  that a default constructor has no statements in its body, not just that it exists.
  This is critical for Spoon's CtClass API where addDefaultConstructor() creates a
  constructor but its body may not be empty if implicit super() is treated as a statement.
code_tags:
- CONSTRUCTOR_BODY_EMPTINESS
- STATE_MUTATION
- INHERITANCE_CHECK
test_pattern: STATE_TEST
---

# default-constructor-is-empty-body

## Instructions

# Default Constructor Body Emptiness Validation

## Instructions

- WHEN the TG encounters code that generates, validates, or tests default constructors (e.g., `addDefaultConstructor()`, `isDefaultConstructor()`, constructor body inspection)
- THEN the TG should test that when a class has no explicit constructors and a default constructor is generated, the generated constructor's body is correctly recognized as **empty** (having zero statements). The test should:
  1. Create a simple class with no explicit constructors
  2. Add a default constructor via the API (e.g., `CtClass.addDefaultConstructor()`)
  3. Retrieve the constructor (e.g., `CtClass.getConstructors()`)
  4. Assert that the constructor's body exists (non-null)
  5. Assert that the constructor's body has exactly 0 statements: `assertTrue(body.getStatements().isEmpty())`
  6. Verify the method being tested respects this emptiness (e.g., methods like `isDefaultConstructor()` should return `true` when the body is empty)
- Include concrete assertion checks: use `assertEquals(0, body.getStatements().size())` or `assertTrue(body.getStatements().isEmpty())`
- **Common pitfalls to avoid**:
  - ❌ Testing only that a constructor exists without checking its body emptiness
  - ❌ Assuming that an implicit `super()` call is not a statement — it may be added as a statement, making the body non-empty
  - ❌ Testing with classes that have explicit constructors (they should not be treated as default)
  - ❌ Only testing the "happy path" where a class has no constructors; also test that adding a default constructor to a class that already has one does not create duplicates

### Correct Example (flows naturally):
```java
// Create a simple class with no constructors
CtClass<?> clazz = factory.Class().get("MyClass");
// Add the default constructor
CtConstructor<?> defaultCons = clazz.addDefaultConstructor();
// Verify the constructor body is empty
assertNotNull(defaultCons.getBody());
assertTrue(defaultCons.getBody().getStatements().isEmpty());
// Verify the method recognizes it as default
assertTrue(clazz.getConstructors().toList().get(0).isDefaultConstructor());
```

### Incorrect Example (what the TG might write without this skill):
```java
// ❌ Only checks that a constructor exists, not that body is empty
CtClass<?> clazz = factory.Class().get("MyClass");
CtConstructor<?> cons = clazz.addDefaultConstructor();
assertNotNull(cons);  // Not enough!
// Missing: assert that the body is empty
// The bug occurs when addDefaultConstructor() creates a constructor
// but its body is treated as non-empty (e.g., has an implicit super() statement)
```