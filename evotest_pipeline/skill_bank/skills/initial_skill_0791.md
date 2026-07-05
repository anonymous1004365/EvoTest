---
name: shell-classloader-configuration-validation
description: When validating shell plugin configuration commands that instantiate
  classes via a ClassLoader (provided by getClassLoader()), test that the ClassLoader
  is properly configured to load the plugin classes. This skill catches bugs where
  a mock or alternative Shell subclass returns a different ClassLoader that lacks
  the required plugin classes.
code_tags:
- VALIDATION
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: PARAMETRIC_TEST
---

# shell-classloader-configuration-validation

## Instructions

# Shell ClassLoader Configuration Validation

## Instructions

- WHEN the TG encounters a Shell plugin configuration command (e.g., `FormatterCommand`, `ShellPluginConfigurationCommand`) that loads a user-specified plugin class (e.g., implementing `Formatter`) by calling `shellState.getClassLoader(cl, shellState)`
- THEN the TG should write a test that verifies the shell can configure the plugin without errors using **both**:
  1. A shell whose `getClassLoader()` returns `ShellPluginConfigurationCommand.class.getClassLoader()` (the production ClassLoader with access to Accumulo classes)
  2. A shell whose `getClassLoader()` returns `MockShell.class.getClassLoader()` (a mock/simplified ClassLoader that may not have access to production plugin classes)
- The test should expect that `configuredPluginClass == pluginClass` (the class loaded via the shell's ClassLoader equals the expected class by reference) and verify that no `ClassNotFoundException` or `IllegalArgumentException` is thrown during plugin configuration
- Common pitfalls to avoid:
  - Testing with only the production Shell subclass without also testing with MockShell or an alternative Shell subclass that provides a different ClassLoader
  - Assuming the ClassLoader returned by `getClassLoader()` always has access to all Accumulo classes — it may be restricted (e.g., `MockShell` returns `MockShell.class.getClassLoader()` which may lack `Formatter` implementations)
  - Only testing that `configuredPluginClass.getName()` equals the expected class name — test that the class objects are equal by reference (`==`) or at least that no `ClassNotFoundException` is thrown during loading
  - Forgetting to test the negative case: a Shell that provides a restrictive ClassLoader should fail to configure the plugin, throwing a `ClassNotFoundException` or causing the configuration to complete with a null/error state

### Example (Incorrect — only tests production Shell):
```java
Shell shell = new Shell(...);
String tableName = "testTable";
// Only tests production path — misses the MockShell bug
assertNotNull(FormatterCommand.getCurrentFormatter(tableName, shell));
```

### Example (Correct — tests both production and mock ClassLoaders):
```java
// Production Shell path
Shell prodShell = new Shell(...);
ClassLoader prodLoader = prodShell.getClassLoader(cl, prodShell);
Class<? extends Formatter> formatterClass = prodLoader.loadClass(className).asSubclass(Formatter.class);
assertNotNull("Production shell should load formatter", formatterClass);

// Mock Shell path — should also work or at least not throw unexpected errors
MockShell mockShell = new MockShell(...);
ClassLoader mockLoader = mockShell.getClassLoader(cl, mockShell);
try {
    Class<? extends Formatter> mockFormatterClass = mockLoader.loadClass(className).asSubclass(Formatter.class);
    assertNotNull("Mock shell should also load formatter", mockFormatterClass);
} catch (ClassNotFoundException e) {
    fail("Mock shell ClassLoader should have access to plugin classes: " + e.getMessage());
}
```