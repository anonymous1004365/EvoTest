---
name: map-type-parameter-diagnostic-message
description: When building diagnostic messages for missing plugin parameters, Map
  types should generate `<KEY>VALUE</KEY>` hints. This skill teaches how to test that
  Map-type parameters produce correct user-facing error messages in PluginParameterException.buildDiagnosticMessage().
code_tags:
- MISSING_MAP_COLLECTION_PARAMETER_MESSAGE
test_pattern: STATE_TEST
---

# map-type-parameter-diagnostic-message

## Instructions

# Map Type Parameter Diagnostic Message Verification

## Instructions

WHEN the TG encounters code that builds diagnostic/error messages for missing plugin parameters (e.g., `PluginParameterException.decomposeParameterIntoUserInstructions()` or `buildDiagnosticMessage()`), where the parameter type can be `java.util.Map`, `java.util.Properties`, `java.util.Collection` subtypes (`java.util.List`, `java.util.Set`), or array types (`java.lang.String[]`):

1. **THEN** the TG MUST test that for `java.util.Map` type parameters, the diagnostic message contains the pattern `<KEY>VALUE</KEY>` (not `<item>VALUE</item>`).

2. **THEN** the TG MUST test that for `java.util.List` (Collection subtype) type parameters, the diagnostic message contains `<item>VALUE</item>`.

3. **THEN** the TG MUST test that for `java.util.Properties` type parameters, the diagnostic message contains `<property>`/`<name>`/`<value>` elements.

4. **THEN** the TG MUST create a `MojoDescriptor` with a non-null `PluginDescriptor` (with `setGoalPrefix()` and `setArtifactId()` set) and a non-null `getGoal()` value before creating the exception.

5. **THEN** the TG MUST create a `Parameter`, set its type using `setType("java.util.Map")` (exact FQN), set its name, mark it as required via `setRequired(true)`, and pass it in a singleton list to `PluginParameterException`.

6. **THEN** the TG MUST call `exception.buildDiagnosticMessage()` and compare the full output string using `assertEquals()` with the expected message.

**Common pitfalls to avoid:**
- **Do not** assume type detection works through generics or raw names — use the exact fully-qualified class name `"java.util.Map"` for the parameter type.
- **Do not** forget to set both `PluginDescriptor` (with `setGoalPrefix()` and `setArtifactId()`) and `MojoDescriptor` (with `setGoal()` and `setPluginDescriptor()`), otherwise the message will be incomplete or NPE.
- **Do not** forget that Map type parameters should use `<KEY>VALUE</KEY>` format, NOT `<item>VALUE</item>` (which is for Collection/array types).
- **Do not** test with partial string matches (`assertTrue(message.contains(...))`) — compare the full expected message with `assertEquals()` to ensure the exact formatting is correct.
- **Do not** omit the trailing `".\n"` in the expected string — the diagnostic message ends with a newline after the configuration block.

**Correct example for Map type:**
```java
public void testMissingRequiredMapTypeParameter() {
    MojoDescriptor mojoDescriptor = new MojoDescriptor();
    mojoDescriptor.setGoal("goal");
    PluginDescriptor pluginDescriptor = new PluginDescriptor();
    pluginDescriptor.setGoalPrefix("goalPrefix");
    pluginDescriptor.setArtifactId("artifactId");
    mojoDescriptor.setPluginDescriptor(pluginDescriptor);

    Parameter parameter = new Parameter();
    parameter.setType("java.util.Map");
    parameter.setName("toAddresses");
    parameter.setRequired(true);

    PluginParameterException exception =
        new PluginParameterException(mojoDescriptor, Collections.singletonList(parameter));

    assertEquals(
        "One or more required plugin parameters are invalid/missing for 'goalPrefix:goal'\n" +
        "\n" +
        "[0] Inside the definition for plugin 'artifactId', specify the following:\n" +
        "\n" +
        "<configuration>\n" +
        "  ...\n" +
        "  <toAddresses>\n" +
        "    <KEY>VALUE</KEY>\n" +
        "  </toAddresses>\n" +
        "</configuration>.\n",
        exception.buildDiagnosticMessage());
}
```

**Incorrect example (likely to pass on buggy code that misidentifies Map types):**
```java
// WRONG: uses assertTrue instead of assertEquals, missing trailing newline
String msg = exception.buildDiagnosticMessage();
assertTrue(msg.contains("<KEY>VALUE</KEY>"));  // Too loose — won't catch formatting issues
```