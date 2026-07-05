---
name: execfile-command-handling-messages
description: When testing shell execfile commands with invalid commands, ensure that
  the shell properly reads all output from the execfile execution and that the output
  contains the expected messages. This applies when executing a file containing unknown
  or invalid commands via the execfile mechanism.
code_tags:
- VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: INTERACTION_TEST
---

# execfile-command-handling-messages

## Instructions

# ExecFile Command Handling and Message Verification

## Instructions

- WHEN the TG encounters a test that executes a shell script file via `execfile` or `exec` command containing invalid commands (e.g., `execfile /path/to/file`)
- THEN the TG should verify that the shell properly reads and reports error messages from the execfile execution by:
  1. Creating a test that writes commands (including an invalid/unknown command like "foo") into a temporary file
  2. Executing the file via the shell's `execfile` command
  3. Reading the shell's full output (using `getOutput()`) after the execfile execution completes
  4. Asserting that the output contains the expected error message (e.g., `assertTrue(output.contains("Unknown command \"foo\""))`)
- Include concrete values/examples: the invalid command string should be `"foo"` and the expected error message should contain `"Unknown command \"foo\""` on the buggy version
- Common pitfalls to avoid:
  - Do NOT assume that the shell automatically displays error messages for unknown commands encountered during execfile — the test must explicitly read `getOutput()` to verify the message appears
  - Do NOT forget to read output AFTER executing the execfile command and before closing the shell
  - Do NOT test with a known valid command instead of an invalid one — the purpose is to verify unknown command handling
  - Do NOT skip creating a temporary file with the invalid command — the execfile command reads commands from a file

### Example (Correct Approach)

```java
// Create a temporary file with an invalid command
File tmpFile = File.createTempFile("test", ".conf", new File(rootPath));
PrintWriter writer = new PrintWriter(tmpFile);
writer.println("foo");  // unknown command
writer.close();

// Execute the file via execfile
ts.exec("execfile " + tmpFile.getAbsolutePath(), true, Constants.VERSION);

// Read all output from the shell
String output = ts.getOutput();

// Verify the error message for the unknown command appears
assertTrue("Expected error message not found in: " + output,
    output.contains("Unknown command \"foo\""));
```

### Example (Incorrect Approach)

```java
// ❌ WRONG: Does not read output and verify the unknown command message
File tmpFile = File.createTempFile("test", ".conf", new File(rootPath));
PrintWriter writer = new PrintWriter(tmpFile);
writer.println("foo");
writer.close();

// Just executes without checking output
ts.exec("execfile " + tmpFile.getAbsolutePath(), true, Constants.VERSION);
// Missing: String output = ts.getOutput();
// Missing: assertTrue(output.contains("Unknown command \"foo\""));
```