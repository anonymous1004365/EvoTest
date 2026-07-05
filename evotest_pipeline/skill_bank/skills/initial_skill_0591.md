---
name: package-reference-replacement-type-consistency
description: When replacing one package reference with another in a code model, the
  TG must ensure all affected type references and related model elements are consistently
  updated. This skill applies when testing package replacement operations that involve
  type references, imports, or qualified names.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# package-reference-replacement-type-consistency

## Instructions

# Package Reference Replacement — Type Consistency

## Instructions

- WHEN the TG encounters a method that replaces a package reference (e.g., `replacePackageReference(PackageRef old, PackageRef new)`) in a code element's model,
  - THEN it should verify that **all affected type references** (e.g., `CtTypeReference`, `CtTypeAccess`, `CtImport`, etc.) contained within the replaced package are updated to reflect the new package, not just the top-level package reference itself.
  - Specifically, when old package `A.B` is replaced by new package `C.D`, any `CtTypeReference` whose (fully qualified name, "qualifiedName") starts with `"A.B"` should have its qualified name updated to start with `"C.D"` after the replacement.

- WHEN testing a package replacement operation,
  - THEN create test scenarios where:
    1. A `CtPackage` (or `PackageRef`) is replaced with another package reference.
    2. The subtree below that package contains **multiple types** (e.g., class `A.B.SomeClass`, `A.B.OtherClass`).
    3. The test should **verify the state** of those types' type references after replacement by asserting that their qualified names reflect the new package (e.g., assert that `someTypeRef.getQualifiedName()` equals `"C.D.SomeClass"`).

- WHEN validating that type references have been correctly updated,
  - THEN also check that other model elements like `CtImport`, `CtTypeAccess`, and any `String`-based qualified name representations have been updated — not just the top-level `CtPackage` reference.

- Common pitfalls to avoid:
  - ❌ *Testing only that the top-level package reference was replaced* (e.g., checking `oldPackage.getSimpleName()`), without verifying that child type references were updated.
  - ❌ *Testing with only a single type* under the package — this can miss bugs where only the top-level reference is updated while deeper references remain unchanged.
  - ❌ *Using String-based assertions that don't capture the full qualified name transformation* — e.g., asserting a partial match that accidentally passes even when the replacement was incomplete.

### Correct Example

```java
// Given a package 'oldPkg' with simple name "oldpkg" containing class "oldpkg.SomeClass"
// When replacing it with package 'newPkg' with simple name "newpkg"
oldPkg.replacePackageReference(newPkg.getReference());

// Then: verify all nested type references are updated
CtTypeReference<?> typeRef = someClass.getReference();
assertEquals("newpkg.SomeClass", typeRef.getQualifiedName());
```

### Incorrect Example (What to Avoid)

```java
// ❌ Only checks the package itself, not child types
oldPkg.replacePackageReference(newPkg.getReference());
assertEquals("newpkg", oldPkg.getSimpleName());  // This passes even if child types broken!
```

### Test Pattern

Use a **STATE_TEST**: perform the replacement operation, then query the state of affected type references, imports, and accesses to verify they were consistently updated. Assert the post-condition state of multiple model elements, not just the top-level package.