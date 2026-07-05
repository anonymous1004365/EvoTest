---
name: module-info-comment-parsing
description: When parsing module-info.java files, comments within the module declaration
  can cause parsing failures. This skill teaches how to create tests that ensure comments
  inside module declarations are handled correctly.
code_tags:
- MODULE_INFO_JAVA_PARSING
test_pattern: PARAMETRIC_TEST
---

# module-info-comment-parsing

## Instructions

# Module-Info Comment Parsing

## Instructions

- WHEN the TG encounters code that creates or parses a `module-info.java` file (e.g., `spoon.test.module.TestModule`)
- THEN it should test that comments within a `module-info.java` module declaration body are correctly parsed
- Specifically, the test should create a `module-info.java` file containing a module declaration with block comments (`/* ... */`) and line comments (`// ...`) embedded inside the module body (before/after `requires`, `exports`, etc.)
- The test should verify that the compiled module-info (e.g., a `CtModule` or equivalent model) has the correct number of module directives (e.g., `requires`, `exports`, `provides`, `opens`, `uses`) — these should NOT be dropped or modified
- Run the test against the buggy version to confirm it FAILS (e.g., number of directives does not match the expected count)
- Common mistake: testing only a clean `module-info.java` without comments, or placing comments only outside the module declaration body. The key is comments INSIDE the body, between directives.
- Example correct test pattern:
  ```java
  // Create a module-info.java with comments inside the module body
  String moduleInfo = "module com.example {\n" +
      "    /* A block comment */\n" +
      "    requires java.base;\n" +
      "    // A line comment\n" +
      "    exports com.example.api;\n" +
      "}\n";
  // Parse it and verify directives count
  CtModule module = launcher.parseModule(moduleInfo);
  assertEquals(2, module.getDirectives().size());
  ```
- Example wrong pattern (would NOT catch the bug):
  ```java
  // Only testing module-info.java without comments
  String moduleInfo = "module com.example {\n" +
      "    requires java.base;\n" +
      "    exports com.example.api;\n" +
      "}\n";
  // This passes in both buggy and fixed versions
  ```
- The bug specifically causes directives AFTER a comment to be lost or miscounted — so asserting the exact directive count or set of directive types is essential.