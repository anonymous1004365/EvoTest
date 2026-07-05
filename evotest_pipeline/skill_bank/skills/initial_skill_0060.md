---
name: pretty-printer-line-output-consistency
description: ''
code_tags:
- NULL_CHECK
- STATE_MUTATION
- TYPE_REFERENCE_EQUALS
test_pattern: STATE_TEST
---

# pretty-printer-line-output-consistency

## Instructions

# Pretty‑Printer Line Output Consistency

## Instructions

- WHEN the TG encounters a pretty‑printer or code‑rendering method that transforms an AST (e.g., `CtModel`, `CtType`, `CtElement`) into source text (typically via a method like `printType`, `printModel`, `prettyprint`, `toString`, or similar),  
  THEN it should **create a test that**:
  1. **Parses a known source file** (e.g., from `src/test/resources`) into an AST model using the project’s parser/factory.
  2. **Calls the pretty‑printer** to obtain the rendered output as a `String`.
  3. **Compares the output to the original source content** (read from the same file).  
     The comparison can be either a direct `assertEquals(originalSource, printedOutput)` or a line‑by‑line comparison.

- WHEN the test asserts on the rendered string,  
  THEN **prefer comparing the full output** against the file content (or an expected result string) rather than checking isolated fragments.  
  *Common pitfall*: Checking only partial output (e.g., a single method signature) may miss formatting errors or missing lines in other parts of the type.

- WHEN the pretty‑printer uses a `DefaultJavaPrettyPrinter` or a custom `PrinterTokenStream` / line‑writing mechanism,  
  THEN the test should also **verify that no `NullPointerException` is thrown** when the printer processes elements such as fields, methods, annotations, or type references — especially when the source has unusual constructs (e.g., inner classes, lambdas, annotations on parameters, or generics).

- **Common pitfalls**:
  - **Not resetting the printer state**: Some pretty‑printers accumulate state (e.g., line numbers, indent levels) across calls. If the printer is reused, reset it before generating output for a new element.
  - **Assuming the output is identical to input**: Normalized ASTs may produce slightly different whitespace. Use line‑by‑line trimming or a whitespace‑tolerant comparison if needed, but prefer exact match for bug detection.
  - **Testing only on trivial types**: Use real‑world source files with multiple methods, annotations, generics, and inner classes to exercise full rendering paths.

- **Correct example** (Java / JUnit 5):
  ```java
  @Test
  void testPrettyPrinterWithLines() {
      // given
      Launcher launcher = new Launcher();
      launcher.addInputResource("./src/test/resources/sample/SomeClass.java");
      CtModel model = launcher.buildModel();
      CtType<?> type = model.getType("sample.SomeClass");
  
      // when
      String printed = launcher.getPrettyPrinter().printType(type);
  
      // then
      String original = new String(
          Files.readAllBytes(Paths.get("./src/test/resources/sample/SomeClass.java")),
          StandardCharsets.UTF_8
      );
      assertEquals(original, printed);
  }
  ```

- **Incorrect example** (missing full comparison, no printer reset):
  ```java
  @Test
  void testPrettyPrinterPartial() {
      Launcher launcher = new Launcher();
      launcher.addInputResource("./src/test/resources/sample/SomeClass.java");
      CtModel model = launcher.buildModel();
      CtType<?> type = model.getType("sample.SomeClass");
  
      // Only checks that printing doesn't throw — does not assert output content
      String printed = launcher.getPrettyPrinter().printType(type);
      assertNotNull(printed);
  
      // Missing: full output comparison would catch bugs like missing newlines,
      // empty lines, or truncated output
  }
  ```