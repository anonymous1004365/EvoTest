---
name: annotation-parameter-index-shift-for-nested-types
description: When processing method parameter annotations with ASM, the index passed
  to visitParameterAnnotation must account for a shift when the method's enclosing
  type adds implicit parameters. The TG should test that annotation parameter indices
  are correctly mapped when a method has fewer visible or invisible parameters than
  total arguments in its descriptor, such as for anonymous or local class constructors.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# annotation-parameter-index-shift-for-nested-types

## Instructions

# Annotation Parameter Index Shift for Non-Enclosed Types

## Instructions

- WHEN the TG encounters an ASM `AnnotationVisitor` implementation that processes a method descriptor for a type that may be anonymous, local, or non-enclosed (e.g., a constructor for an anonymous class defined inside a method), AND the code handles `visitAnnotableParameterCount(int count, boolean visible)`, AND the code computes an index for `visitParameterAnnotation(int index, String descriptor, boolean visible)`
- THEN the TG should test the scenario where a method (like `<init>`) has a descriptor with more argument types than the number of annotated parameters reported by `visitAnnotableParameterCount`. Specifically:
  1. Create a test that creates a `TypePool.Default` (or analogous ASM-based type pool/annotation extractor)
  2. Look up a type description that is an anonymous or non-enclosed type defined within a method
  3. Verify that parameter annotations on that type's constructor are correctly resolved without throwing any exception (e.g., no `IndexOutOfBoundsException`, no `NullPointerException`)
  4. Verify that the returned annotation values match the expected annotation on the correct parameter position
- Include concrete values: test with a parameter annotation on the first (index 0) parameter of an anonymous class constructor whose enclosing method has an implicit `this` parameter in the descriptor. For example, the descriptor `(Ljava/lang/Object;I)V` has 2 argument types but if `visitAnnotableParameterCount(1, true)` is called (only 1 visible parameter), then the visible parameter index 0 should map to descriptor argument index 1 (not 0), and the test should verify this mapping is correct.
- **Common pitfalls to avoid**:
  - **Pitfall 1**: Testing only with top-level classes where parameter counts match descriptor arguments exactly — this will not exercise the shift logic.
  - **Pitfall 2**: Assuming `visitParameterAnnotation`'s `index` parameter directly matches the method descriptor's argument index without considering the shift from `visitAnnotableParameterCount`.
  - **Pitfall 3**: Only testing with `visible = true` parameters and forgetting that `invisible = false` parameters also need their own independent shift.
  - **Pitfall 4**: Not testing the scenario where acquiring the type description itself (e.g., calling `typePool.describe(...)`) throws an exception due to the incorrect index mapping.