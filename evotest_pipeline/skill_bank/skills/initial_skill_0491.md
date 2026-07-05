---
name: reporting-exclude-defaults-inheritance
description: When merging Reporting model elements during POM inheritance, the `excludeDefaults`
  Boolean field must be explicitly merged from parent to child. This skill teaches
  how to test that all Reporting fields are properly inherited during model merging.
code_tags:
- VALIDATION
- INHERITANCE_PROPERTY_MERGE
test_pattern: STATE_TEST
---

# reporting-exclude-defaults-inheritance

## Instructions

# Reporting ExcludeDefaults Inheritance Verification

## Instructions

- WHEN the TG encounters code that merges a `Reporting` object from a parent POM into a child POM (e.g., in `ModelMerger.mergeReporting()` or `DefaultModelInheritanceAssembler`),
- THEN the TG should verify that **every** field of the `Reporting` model, especially `excludeDefaults` (a `Boolean`), is properly inherited from parent to child during merge. The test should:
  1. Create a parent `Reporting` model with `excludeDefaults` set to `Boolean.TRUE`
  2. Create a child `Reporting` model with `excludeDefaults` set to `null` (default)
  3. Invoke the merge operation with `sourceDominant=true` (parent as source)
  4. Assert that after merge, the child's `getExcludeDefaults()` returns `Boolean.TRUE`
  5. Also test the reverse: set child's `excludeDefaults` to `Boolean.FALSE` and parent to `Boolean.TRUE`, then verify the correct dominance behavior
- Common pitfalls to avoid:
  - Testing only `String` or `List` fields while omitting `Boolean` fields like `excludeDefaults`
  - Assuming that because `mergeReporting_ExcludeDefaults()` exists in the code, it is actually called — verify the merge method invocation chain
  - Testing with `boolean` primitive instead of `Boolean` object — `null` state matters for merge semantics

### Correct Example
```java
@Test
public void testReportingExcludeDefaultsInheritance() {
    Reporting parent = new Reporting();
    parent.setExcludeDefaults(true);
    Reporting child = new Reporting();
    // child.excludeDefaults remains null
    
    ModelMerger merger = new ModelMerger();
    merger.mergeReporting(child, parent, true, null);
    
    assertTrue("excludeDefaults should be inherited from parent",
        child.isExcludeDefaults());
}
```

### Incorrect Example
```java
// BAD: Only testing output/plugins merge, ignoring excludeDefaults
@Test
public void testReportingMerge() {
    Reporting parent = new Reporting();
    parent.addOutput("info");
    parent.addPlugin(plugin);
    Reporting child = new Reporting();
    mergeReporting(child, parent, true, null);
    // Missing assertion on excludeDefaults
}
```