---
name: java-lang-implicit-import-validation
description: Helps detect bugs where java.lang types are incorrectly flagged as needing
  explicit imports. When a type from java.lang (e.g., String, Integer, Thread) is
  present in code but not imported, these tests validate that the type is still correctly
  recognized as implicitly imported per JLS rules.
code_tags:
- NULL_CHECK
- VALIDATION
- EDGE_CASE_INPUT
test_pattern: STATE_TEST
---

# java-lang-implicit-import-validation

## Instructions

# Java Lang Implicit Import Validation

## Instructions

WHEN the TG encounters code that checks whether types are "imported" or "considered as imported" in a source code model (e.g., a `getImports()` or `isImported()` method or any logic that classifies types from source files as imported vs. not imported),

THEN the TG should:
1. Create a test that adds a type from the `java.lang` package (such as `String`, `Integer`, `System`, `Thread`, `Math`, etc.) to a source file being processed, but does NOT add any explicit import statement for that type.
2. Verify that the code under test considers the `java.lang` type as imported even though no explicit import exists for it.
3. Also test with a non-`java.lang` type (e.g., `java.util.List`, `java.io.File`, or a custom class) without an import to verify it is correctly NOT considered imported.
4. Compare the outcome: the `java.lang` type should be considered imported while the other type should not.

Be specific about the method signatures involved. For instance, if testing a method like `isImported(CtTypeReference<?> ref)`, `getImport(String name)`, or `isConsideredAsImported(CtTypeReference<?> ref)`, call it directly with type references created from `java.lang.String`, `java.lang.Integer`, etc.

**Common pitfalls to avoid:**
- ❌ Only testing with non-`java.lang` types, thus missing the implicit import behavior.
- ❌ Providing explicit imports for `java.lang` types (which is not required by the JLS and might cause false positives/negatives).
- ❌ Testing with string names instead of proper type references (`CtTypeReference`).
- ❌ Asserting the wrong boolean value (the `java.lang` type should be considered imported, not the opposite).

**Correct approach example:**
```java
// Create a factory
CtTypeReference<String> stringRef = factory.Type().createReference(String.class);
// No import added for java.lang.String
assertTrue("java.lang.String should be considered imported without explicit import", 
    importHelper.isConsideredAsImported(stringRef));
```

**Incorrect approach example:**
```java
// Testing only with java.util types
CtTypeReference<List> listRef = factory.Type().createReference(ArrayList.class);
assertFalse(importHelper.isConsideredAsImported(listRef)); // Correct, but doesn't test java.lang behavior
// Missing the crucial java.lang.String test!
```

**What to expect on the buggy version:**
The buggy code may incorrectly return `false` for `java.lang` types that have no explicit import, or may not differentiate between `java.lang` types and other implicit imports. Expect an assertion failure (e.g., `AssertionError` or `AssertionFailedError`) on the `assertTrue` for a `java.lang` type.