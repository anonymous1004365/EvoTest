---
name: properties-type-user-instruction
description: When generating user-facing configuration help messages that distinguish
  between Collection, Map, and Properties types, ensure Properties type detection
  uses isAssignableFrom and is not accidentally placed after Map in the branch order,
  causing Properties to be mislabeled as Map.
code_tags:
- NULL_CHECK
- CONDITIONAL_BRANCH
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# properties-type-user-instruction

## Instructions

# Properties Type User-Instruction Generation

## Instructions

- WHEN the TG encounters code that generates user-facing configuration instructions (e.g., XML snippet templates) and uses `Class.forName()` with `isAssignableFrom()` checks to detect parameter types (e.g., `Collection`, `Map`, `Properties`)
- THEN the TG should write a test that verifies the correct instruction format for **each type variant**: `String[]`, `java.util.List`, `java.util.Map`, AND `java.util.Properties`
  - For `java.util.Properties`, the expected output should contain `<property>`, `<name>KEY</name>`, and `<value>VALUE</value>` in the generated message (NOT `<KEY>VALUE</KEY>` which is the Map format)
  - Use `assertEquals(expectedMessage, exception.buildDiagnosticMessage())` to compare the full diagnostic message
  - Set `parameter.setRequired(true)` and use a `MojoDescriptor` with a `PluginDescriptor` that has `goalPrefix` and `artifactId` set
- Common pitfalls:
  - Testing only with `String[]`, `List`, or `Map` types but forgetting to test `Properties` — the bug is that Properties falls through to the Map branch if the Properties check is missing or placed after Map
  - Using `Mockito` to mock the `Parameter` object; the `Parameter` must be a real instance with `setType()` and `setName()` called, so that `getType()` returns the expected fully-qualified class name for `Class.forName()`

### Correct Example
```java
Parameter parameter = new Parameter();
parameter.setType("java.util.Properties");
parameter.setName("toAddresses");
parameter.setRequired(true);

PluginParameterException exception =
    new PluginParameterException(mojoDescriptor, Collections.singletonList(parameter));

assertEquals(
    "One or more required plugin parameters are invalid/missing for 'goalPrefix:goal'\n\n" +
    "[0] Inside the definition for plugin 'artifactId', specify the following:\n\n" +
    "<configuration>\n  ...\n  <toAddresses>\n" +
    "    <property>\n      <name>KEY</name>\n      <value>VALUE</value>\n" +
    "    </property>\n  </toAddresses>\n</configuration>.\n",
    exception.buildDiagnosticMessage());
```

### Incorrect Example (would pass with buggy code, missing Properties handling)
```java
// This only tests Map, not Properties — the buggy code would pass this test
Parameter parameter = new Parameter();
parameter.setType("java.util.Map");
parameter.setName("toAddresses");
```