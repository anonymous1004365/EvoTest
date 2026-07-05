---
name: restrict-import-type-selection
description: When managing automatic imports for static members in pretty-printing,
  ensure the test verifies that imports are restricted to only the specific types
  directly referenced in the code rather than their supertypes. This skill applies
  when testing import computation logic that filters static imports.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- IMPORT_HANDLING_STATIC
test_pattern: PARAMETRIC_TEST
---

# restrict-import-type-selection

## Instructions

# Restrict Import Type Selection

## Instructions

- WHEN the TG encounters code that computes automatic imports for static methods/fields (e.g., in a pretty printer's auto-import mode)
- THEN it should verify that an import is only added when the **exact type** containing the static member appears in the code's imports, not any of its supertypes.
  - Concretely: if code uses `ChildClass.staticMethod()`, and `ChildClass` extends `ParentClass` which also defines the same static method, then only `import static ChildClass.staticMethod` should be deemed useful — importing `ParentClass.staticMethod` must be rejected as "useless."
  - The test should set up a test case where a class inherits a static member from its parent, then only references the child type, and assert that the import is either "not imported" (treated as useless) or only the child's import is used.
  - Verify that the import set computed by the auto-import logic does **not** contain `ParentClass.staticMethod` when the code only uses `ChildClass.staticMethod`.
  - Use the pretty printer's auto-import mode configuration to trigger the computation.
- Common pitfalls to avoid:
  - Testing only with direct type references (no inheritance) — this would not expose the bug.
  - Assuming that a static member imported from a supertype is considered "used" simply because it exists in the hierarchy.
  - Forgetting to configure the pretty printer's auto-import mode before running assertions.
  - Relying on implicit imports or default settings without explicitly setting auto-import mode.

### Example (correct approach)

```java
// Given a class ChildClass extends ParentClass, and ParentClass defines staticMethod():
// Code under test uses only ChildClass.staticMethod(...)

AutoImportOptions options = new AutoImportOptions();
options.setMode(ImportMode.ALL_CLASSES_AND_PACKAGES);
PrettyPrinter printer = new DefaultJavaPrettyPrinter(env, options);
// ... set up the code snippet ...
String result = printer.print();

// Then: assert that the import for ChildClass.staticMethod is generated,
// and the import for ParentClass.staticMethod is NOT generated.
assertThat(result, not(containsString("import static ParentClass.staticMethod")));
```

### Example (incorrect approach)

```java
// WRONG: Tests only direct type references without inheritance
AutoImportOptions options = new AutoImportOptions();
options.setMode(ImportMode.ALL_CLASSES_AND_PACKAGES);
// ... only uses MyClass.myMethod() where MyClass is the declaring type ...
// This test passes even on the buggy version and does not detect the regression.
assertTrue(result.contains("import static MyClass.myMethod"));
```