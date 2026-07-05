---
name: plugin-collection-state-mutation-testing
description: When testing collection-backed model builders that mutate state (add/remove
  elements) on model objects, test that internal state transformations produce the
  correct final model rather than just intermediate or partial state. This skill applies
  to build lifecycle phases where plugins, dependencies, or other elements are injected/manipulated
  programmatically.
code_tags:
- VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# plugin-collection-state-mutation-testing

## Instructions

# Plugin/Dependency Collection State Mutation Testing

## Instructions

- WHEN the TG encounters a model builder or project construction class that programmatically adds plugins, dependencies, or other elements to a Maven model (e.g., `Model`, `Build`, `PluginManagement`) via methods like `addPlugin`, `addDependency`, or direct collection mutation
- THEN it should write tests that construct a complete POM input model (via `Model`, `MavenProject`, or test resource XML), run it through the full model-building pipeline, and assert on the **final built model** rather than checking intermediate builder outputs or partial state
- WHEN a bug involves elements being added to a collection (e.g., `getPlugins()` or `getDependencies()`) inside a builder's `build()` method but the collection initialization is missing or the injection happens in the wrong phase
- THEN verify by checking numeric properties like `getPlugins().size()`, `getDependencies().size()`, or specific element presences (e.g., `getPlugin("groupId:artifactId")`) on the fully constructed model returned from `new MavenProject(model)` or equivalent
- WHEN testing plugin management or dependency injection scenarios
- THEN ensure the test POM uses the actual XML namespace, model version, and schema expected by the builder (e.g., `http://maven.apache.org/POM/4.0.0`, `xsi:schemaLocation`, `modelVersion 4.0.0`)
- Common pitfalls:
  - Testing only that a builder method returns without error — verify the actual mutated model state (e.g., plugin list size, dependency list content)
  - Relying on intermediate representations or raw `Model` instances before the full injection pipeline has run
  - Constructing test POMs with an incomplete or incorrect XML namespace/schema, causing the builder to silently skip elements
  - Testing with a single element type when the bug involves mixed-type or multi-element collection mutations

### Correct Example (catches the bug)

```java
// Test that pluginManagement plugins are correctly injected into the model
@Test
public void testPluginManagementDependencies() throws Exception {
    Reader reader = new FileReader("src/test/resources/projects/pluginManagement-dependencies.xml");
    Model model = new Xpp3DomBuilder(reader, true).build();
    // Equivalent pipeline: new MavenProject(model) or builder.build(model)
    MavenProject project = new MavenProject(model);
    
    // Assert on the final state — the plugin list should be populated
    assertNotNull("Plugin list should not be null", 
        project.getBuild().getPlugins());
    assertFalse("Plugins should not be empty — pluginManagement should inject them", 
        project.getBuild().getPlugins().isEmpty());
}
```

### Incorrect Example (misses the bug)

```java
// WRONG: Only checks that the builder doesn't throw an exception
@Test
public void testPluginManagementDependencies() throws Exception {
    Reader reader = new FileReader("src/test/resources/projects/pluginManagement-dependencies.xml");
    Model model = new Xpp3DomBuilder(reader, true).build();
    // No assertion on the resulting model state — misses missing plugin injection
}
```