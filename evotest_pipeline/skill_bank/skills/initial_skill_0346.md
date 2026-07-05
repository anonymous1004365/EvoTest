---
name: package-declaration-source-position-validation
description: When testing source positions for package declarations, the TG should
  verify that the source position is set to "(unknown file)" for implicit/generated
  package declarations, not the source file where the package actually appears. This
  skill helps catch bugs where package declaration positions incorrectly point to
  a real source file instead of indicating an unknown/missing source.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# package-declaration-source-position-validation

## Instructions

# Package Declaration Source Position Validation

## Instructions

- WHEN the TG encounters code that handles the **source position of a package declaration** (e.g., `JDTTreeBuilder.computeFakePackageDeclaration()` or similar methods that create/modify `CtPackage` or `CtPackageDeclaration` objects)
  - THEN the TG should test that the **source position** (`SourcePosition`) of the resulting package declaration is set to `"(unknown file)"` (i.e., `SourcePosition.UNKNOWN_POSITION` or equivalent) when no real source file is associated with the package
  - Specifically, verify that `getPosition().getSource() == null` or that the position's source indicates `"(unknown file)"`

- WHEN the TG encounters a test for **package declaration positions**
  - THEN the TG should compare the `SourcePosition` of the package declaration against `SourcePosition.NOPRINT` or test that `getPosition().getSource().getSimpleName()` equals `"(unknown file)"`
  - The test should verify that the position **does NOT** point to the actual test class file (e.g., not `"Foo.java:3"` or similar)

- WHEN the TG writes a test for package declaration position
  - THEN **include two test scenarios**:
    1. **Explicit package declaration** (e.g., `package foo;` in a source file) — position should point to the actual source file
    2. **Implicit/generated package declaration** (e.g., a package declaration created by the framework for a type that has no explicit package statement) — position should be `"(unknown file)"` or `SourcePosition.UNKNOWN_POSITION`

### Common Pitfalls

- ❌ Testing only that a package declaration has *some* source position, but not checking that the source file is correct
- ❌ Asserting that a generated package declaration's source position points to a real `.java` file when it should point to `"(unknown file)"`
- ❌ Forgetting to check both the explicit case (where position should be real) and the implicit/generated case (where position should be unknown)
- ❌ Using `assertNotNull` on position without also checking what the source file is

### Correct Example (in pseudo-code)

```java
// Test that generated package declaration has unknown position
CtPackage pack = ...; // package declaration created by framework
assertEquals("(unknown file)", pack.getPosition().getSource().getSimpleName());
assertNull(pack.getPosition().getSource());
```

### Incorrect Example

```java
// BUG: This passes even when position incorrectly points to a real file
CtPackage pack = ...;
assertNotNull(pack.getPosition()); // WRONG: doesn't check what source file is referenced
```