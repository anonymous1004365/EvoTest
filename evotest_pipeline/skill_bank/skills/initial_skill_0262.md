---
name: shell-exec-config-initialization
description: When a Shell-like class has a config object field that may be null, and
  the constructor initializes it from a parameter with the same name, ensure the test
  sets the config before executing commands. Otherwise, NullPointerException occurs
  when config is accessed.
code_tags:
- INPUT_VALIDATION
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# shell-exec-config-initialization

## Instructions

# Shell Exec Config Initialization

## Instructions

- WHEN the TG encounters a class (e.g., `Shell`) that has a **field** (e.g., `ShellConfig` or similar config object) which is set via a constructor parameter that shares the **same name** as the field:
  - THEN the TG should verify that the constructor **correctly assigns** `this.field = field` (not just `field = field` which is a no-op due to variable shadowing).
  - The TG should write a test that:
    1. Creates an instance using the constructor that accepts the config parameter.
    2. Then calls a method that **accesses the config field** (e.g., `getConfig()` or any method that internally reads the config).
    3. Verifies that the config is non-null and properly set (e.g., `assertNotNull(shell.getConfig())`).
    4. On the buggy version, this test fails with a `NullPointerException` or returns `null` unexpectedly.

- WHEN the TG sees a shell-like class with a `setConfig()` method or constructor that takes a config parameter:
  - THEN the TG should test that:
    - Calling `shell.executeCommand("foo")` or similar execution methods works when the config has been set.
    - The shell should NOT throw an exception like `IllegalArgumentException` claiming "Unknown command present in..." simply because the config field was null when the command was parsed.

- **Common pitfalls to avoid**:
  - Testing only with default/no-arg constructors that leave the field null — test the constructor that actually sets the config.
  - Assuming the config is always set before execution — test the scenario where it's not properly initialized and verify the correct error (e.g., NullPointerException vs. meaningless IllegalArgumentException).
  - Not checking that the field assignment actually uses `this.field = value` vs. the shadowing bug `field = value` (which silently fails).

- **Correct example** (test that catches the bug):
  ```java
  @Test
  public void testShellConfigInitialization() {
      ShellConfig config = new ShellConfig();
      Shell shell = new Shell(config);
      assertNotNull("Config should be non-null after constructor", shell.getConfig());
      // Now execution should work
      shell.executeCommand("help"); // should not throw NPE
  }
  ```

- **Incorrect example** (test that misses the bug):
  ```java
  @Test
  public void testShellDefaultConstructor() {
      Shell shell = new Shell(); // leaves config as null
      // Test assumes config is lazy-initialized but it isn't
      shell.executeCommand("help"); // NPE here but test doesn't assert on config
  }
  ```