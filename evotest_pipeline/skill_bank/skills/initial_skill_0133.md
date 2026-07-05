---
name: synthetic-parameter-visibility-shift
description: When a method parameter's visibility/appearance in the parameter list
  depends on its synthetic nature (e.g., synthetic vs non-synthetic), the TG should
  test that all expected parameters are correctly included/excluded in the resulting
  parameter description list. Mismatches can cause silent corruption of method signatures.
code_tags:
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# synthetic-parameter-visibility-shift

## Instructions

# Synthetic Parameter Visibility Handling

## Instructions

- WHEN the TG encounters a method that extracts or builds parameter descriptions from a class file's method debug info (e.g., `MethodVisitor`, `ParameterExtractor`, or custom attribute reading that inspects `synthetic` flags on parameters)
- THEN the TG should write a test that validates parameter indexing is correct when synthetic parameters are interspersed with regular parameters. Specifically:
  - Create a test method that loads a class (real or generated) where the method has a mix of **synthetic and non-synthetic parameters**, where synthetic parameters appear as `invisible` (having a `Synthetic` attribute but no `MethodParameters` attribute entry) while non-synthetic parameters appear as `visible` (having entries in the `MethodParameters` attribute).
  - Verify that the total count of `visible` parameters is correct.
  - Verify that each non-synthetic parameter is mapped to the correct index in the resulting description list.
  - Verify that synthetic parameters do NOT corrupt the mapping of non-synthetic parameters to their indices (i.e., synthetic parameters should not "push" non-synthetic parameters to wrong positions).
  - Expect that a buggy implementation may return an incorrect number of parameters or mis-assign parameter indices (e.g., returning 2 non-synthetic parameters when only 1 is expected, or mapping parameter names to wrong indices).

- Common pitfalls to avoid:
  - **Testing only synthetic parameters or only non-synthetic parameters** — the bug only manifests when both types are present. A test with only synthetic or only non-synthetic parameters will not catch it.
  - **Assuming parameter indices are 0-based** — verify that index computation correctly accounts for parameter visibility.
  - **Using only simple generated classes** — the test must specifically use a class file where the `MethodParameters` attribute and `Synthetic` attribute produce a visibility mismatch (some params visible with names, others invisible/synthetic).
  - **Not checking parameter name-to-index mapping** — the bug might produce the correct count but wrong assignments. Always verify that each named parameter maps to the correct index.
  - **Forgetting to test both the count and the actual parameter objects** — verify that the returned parameter descriptions have the correct names and types.

- Correct example (conceptual):
```java
// Test: method has 3 parameters: 0=synthetic(invisible), 1=nonSynthetic(visible,name="a"), 2=nonSynthetic(visible,name="b")
// Buggy: returns 2 visible params or maps "a" to wrong index
// Fixed: returns 2 visible params, "a" at index 0, "b" at index 1
```

- Incorrect example (would NOT catch the bug):
```java
// Test: only synthetic parameters or only non-synthetic parameters
// Bug: index corruption only happens when synthetic params shift non-synthetic indices
// This test passes on both buggy and fixed versions — no value
```