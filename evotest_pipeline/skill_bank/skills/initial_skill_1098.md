---
name: orphan-field-reference-printing
description: When printing field references that could be orphaned (missing parent
  or declaring type), the pretty printer must handle null values gracefully without
  throwing NullPointerException. This skill applies to AST pretty-printing code that
  traverses and prints field access expressions.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- CLASS_ACCESS_PATH_SCAN
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# orphan-field-reference-printing

## Instructions

# Orphan Field Reference Printing

## Instructions

- WHEN the TG encounters code that pretty-prints a `CtFieldReference` (or similar AST element for field access) by traversing its children (e.g., accessing `getParent()`, `getDeclaringType()`, or iterating over access paths)
- THEN the TG should write a test that creates a field reference with a **null or missing parent/declaring type** (an "orphan" reference) and attempts to print it using the pretty printer
- Verify that the pretty printer does **not** throw a `NullPointerException` when encountering a field reference whose declaring type or parent access path is `null`
- The test must construct the field reference programmatically (e.g., using a `Factory` or `CodeBuilder`) rather than from parsed source code, to simulate the orphaned state
- Common pitfalls to avoid:
  - **Only testing with fully-formed field references** (from parsed source) — these always have valid parent paths and won't trigger the bug
  - **Testing the wrong exception class** — the bug manifests as `NullPointerException` during recursive traversal, not as an assertion failure in output correctness
  - **Only checking top-level field access** — the bug occurs in recursive scanning of the access path's children; test a field reference whose parent chain eventually reaches a null value
  - **Forgetting to exercise the print/scan method** — simply creating the orphan reference is not enough; the test must call the method that traverses it (e.g., `printFieldReference`, `scan`, or pretty-print entry point)

### Example (Correct)

```java
// Construct an orphaned field reference programmatically
CtFieldReference<?> fieldRef = factory.Field().createReference(
    factory.Type().stringType(),  // declaring type
    "someField",                  // field name
    factory.Type().objectType()   // field type
);
// Remove the parent to make it orphaned
((CtFieldReference<?>) fieldRef).setParent(null);
// Or: set a parent whose own parent chain eventually hits null

// Attempt to print it — should NOT throw NPE
PrettyPrinter printer = new DefaultJavaPrettyPrinter(factory.getEnvironment());
printer.calculate(factory.Class().get("SomeClass")); // or similar setup
printer.scan(fieldRef); // or printer.printFieldReference(fieldRef)
```

### Example (Incorrect — won't catch the bug)

```java
// ❌ Only testing from parsed code — these references are never orphaned
CtClass<?> clazz = factory.Class().get("SomeClass");
CtField<?> field = clazz.getField("someField");
printer.scan(field.getReference()); // parent chain is always valid
```

### Example (Incorrect — missing the recursive traversal)

```java
// ❌ Only creating the orphan but not calling the scan/print method
CtFieldReference<?> fieldRef = factory.Field().createReference(...);
((CtFieldReference<?>) fieldRef).setParent(null);
// No call to printer.scan() or printer.printFieldReference()
// The bug won't be triggered without exercising the traversal
```