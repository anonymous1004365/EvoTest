---
name: template-parameter-type-validation
description: When parsing plugin descriptor XML elements that define Mojo template parameters, the TG should test with multiple parameter types (not just String) to verify correct handling. This skill catches bugs where template parameters of non-String types (e.g., MojoFailureException, File) cause parse failures.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'BOUNDARY_CHECK', 'VALIDATION']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that parses XML plugin descriptors (e.g., `PluginDescriptorBuilder`) and populates a collection with template parameter type names from `<parameter>` elements
- THEN the TG should write tests that:
  1. Create a test XML descriptor containing `<parameters>` with template parameters of mixed types — both `String` **and** non-String types like `org.apache.maven.plugin.MojoFailureException` or `java.io.File`
  2. Assert that parsing the descriptor does **NOT** throw a `NullPointerException`, `ClassCastException`, or any other exception
  3. Verify the parsed `MojoDescriptor` contains the expected number of template parameters
  4. Verify each parsed template parameter's implementation type is correctly preserved (not overwritten or nullified)

- **Common pitfalls to avoid:**
  - ❌ Testing only with `String`-type template parameters — this masks the bug because the code works fine for String but fails for other types
  - ❌ Not including `<parameters>` section at all in the test descriptor — the bug only manifests when template parameters of certain types exist
  - ❌ Testing only the happy path without checking that all parameters survive parsing correctly

### Correct Example (what the test should do):
```java
@Test
void testBuildReader() throws Exception {
    String descriptor = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        + "<plugin>"
        + "  <mojos>"
        + "    <mojo>"
        + "      <goal>test</goal>"
        + "      <implementation>some.goal.GoalMojo</implementation>"
        + "      <language>java</language>"
        + "      <parameters>"
        + "        <parameter>"
        + "          <name>param1</name>"
        + "          <type>java.lang.String</type>"
        + "        </parameter>"
        + "        <parameter>"
        + "          <name>param2</name>"
        + "          <type>org.apache.maven.plugin.MojoFailureException</type>"
        + "        </parameter>"
        + "      </parameters>"
        + "    </mojo>"
        + "  </mojos>"
        + "</plugin>";

    PluginDescriptorBuilder builder = new PluginDescriptorBuilder();
    PluginDescriptor result = builder.build(new StringReader(descriptor), null);
    assertNotNull(result);
    List<MojoDescriptor> mojos = result.getMojos();
    assertEquals(1, mojos.size());
    List<String> parameters = mojos.get(0).getParameters();
    assertEquals(2, parameters.size());
    assertEquals("java.lang.String", parameters.get(0));
    assertEquals("org.apache.maven.plugin.MojoFailureException", parameters.get(1));
}
```

### Incorrect Example (what the TG might write without this skill):
```java
// ❌ BAD: Only tests String type, won't catch the bug
@Test
void testBuildReader() throws Exception {
    String descriptor = "<?xml version=\"1.0\"...<type>java.lang.String</type>...";
    PluginDescriptor result = builder.build(new StringReader(descriptor), null);
    assertNotNull(result);
    // passes even on buggy version
}
```