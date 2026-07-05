---
name: pretty-printer-regression-test
description: WHEN the TG encounters a pretty printer or code generation class that
  produces textual output — THEN it should test for output stability and consistency
  by printing a known model and verifying the output matches expected string results
  to catch silent regressions.
code_tags:
- VALIDATION
test_pattern: STATE_TEST
---

# pretty-printer-regression-test

## Instructions

# Pretty Printer Output Consistency

## Instructions

- WHEN the TG encounters a pretty printer class (e.g., `DefaultPrettyPrinter`, `Printer`, or similar code generation that builds a string output token-by-token)
  - AND the printer has methods like `calculate`, `reset`, `getResult`, `write`, `print`, or similar stateful operations that modify internal buffers
  - THEN the TG should write a **state test** that:
    1. Creates a full model (e.g., a `CtPackage` with at least one `CtClass` containing a method with parameters and statements)
    2. Feeds that model through the printer (e.g., via `SpoonModelBuilder` or `Launcher`)
    3. Captures the printed output (e.g., `getResult()`)
    4. Calls `reset()` or equivalent
    5. Prints the same model again
    6. Asserts that both outputs are **identical**, failing with an `AssertionError` if they differ
  - Include concrete expectations: `assertEquals(secondOutput, firstOutput)` to verify idempotency
  - Test **both** the equality of two separate printing runs **and** the idempotency of printing the same model twice in a row on the same printer instance

- Common pitfalls to avoid:
  - **Printing only once**: Testing a single print with no comparison against a second print run will not catch state mutation bugs where the printer changes its internal state after the first invocation
  - **Testing the wrong level**: Testing just a single method signature or annotation rather than a full class/package with multiple elements (methods, parameters, types) — ordering issues only surface with multiple elements
  - **Ignoring reset behavior**: Not calling reset between two print runs on the same printer instance means you only test fresh creation, not re-use of a printer
  - **Not using the actual model builder**: Using a hand-crafted string or custom printer bypass does not test the full pipeline that triggers the bug

### Correct Example (catches the bug):
```java
// Build a full Java model
Launcher launcher = new Launcher();
launcher.addInputResource("./src/test/java/spoon/test/prettyprinter/testclasses/");
launcher.buildModel();

// Create two printers and print the same model
DefaultPrettyPrinter printer1 = new DefaultPrettyPrinter(launcher.getEnvironment());
printer1.calculate(launcher.getModel().getAllTypes(), launcher.getModel());
String result1 = printer1.getResult();

DefaultPrettyPrinter printer2 = new DefaultPrettyPrinter(launcher.getEnvironment());
printer2.calculate(launcher.getModel().getAllTypes(), launcher.getModel());
String result2 = printer2.getResult();

// Both results must be identical
assertEquals(result2, result1);
```

### Incorrect Example (misses the bug):
```java
// Only prints once — no consistency check
Launcher launcher = new Launcher();
launcher.buildModel();
DefaultPrettyPrinter printer = new DefaultPrettyPrinter(launcher.getEnvironment());
printer.calculate(launcher.getModel().getAllTypes(), launcher.getModel());
String result = printer.getResult();
assertNotNull(result);  // Passes even with the bug
```