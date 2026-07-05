---
name: palette-initialize-children-before-model-use
description: When a Palette component's children (Choices, Recorder) have their setChoicesModel/setSelectedModel
  called via Palette.initialize() and the model choice list is mutated after initialization,
  test that list mutations are properly propagated. Use when testing components that
  delegate model initialization to children.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# palette-initialize-children-before-model-use

## Instructions

# Palette Component Initialization and Model Propagation

## Instructions

- WHEN a Palette component (org.apache.wicket.extensions.markup.html.form.palette.Palette) is instantiated and its `initialize()` method is called, which propagates choice models to internal child components (Choices, Recorder) via `setChoicesModel()` and `setSelectedModel()`
- THEN after the component is added to a page and its `onInitialize()` has run, verify that the internal state (e.g., the `choices` list accessible through child components) remains consistent with the original model, even after the model object's list is mutated post-initialization
- Specifically: create a `Palette` with a `ListModel` (e.g., `Model.ofList(...)`) where the list is populated before adding the Palette to the page. Then after the page's `renderHead()` or after `tester.startPage(...)`, modify the underlying list by adding/removing elements, and verify that the Palette's child components do not throw `IndexOutOfBoundsException`, `ConcurrentModificationException`, or silently return stale data
- Common pitfall: testing Palette only with static/detachable models (LoadableDetachableModel) and not with mutable ListModel instances. Also, testing only the Palette directly without rendering it in a page via WicketTester, since the `onInitialize()` flow is critical for the bug to manifest
- The test should use `WicketTester` to start a test page containing the Palette, then after the page renders, mutate the model's backing list and verify no exceptions occur when the Palette's child components access the model
- Verify that no `NullPointerException` or other runtime exception is thrown when the Palette components access their models after model list mutation

### Correct example:

```java
@Test
public void testPaletteWithMutableModel()
{
    // Create a Palette with a mutable ListModel
    List<String> choices = new ArrayList<>(Arrays.asList("A", "B", "C"));
    List<String> selected = new ArrayList<>();
    
    IModel<List<String>> choicesModel = Model.ofList(choices);
    IModel<List<String>> selectedModel = Model.ofList(selected);
    
    Palette<String> palette = new Palette<String>("palette", selectedModel, choicesModel, 
        new ChoiceRenderer<String>("toString"), 5, false) {};

    PaletteTestPage page = new PaletteTestPage(palette);
    tester.startPage(page); // triggers onInitialize -> initialize which propagates models
    
    // Mutate the underlying list AFTER initialization
    choices.add("D");
    choices.remove("A");
    
    // Re-render - should not throw any exception
    tester.executeAll();
    // No exception means success
}
```

### Incorrect example (fails to catch the regression):

```java
@Test
public void testPalette()
{
    // Only testing with LoadableDetachableModel, not testing mutable list mutation
    IModel<List<String>> choicesModel = new LoadableDetachableModel<List<String>>() {
        @Override
        protected List<String> load() {
            return Arrays.asList("A", "B", "C");
        }
    };
    
    Palette<String> palette = new Palette<String>("palette", Model.ofList(new ArrayList<>()), 
        choicesModel, new ChoiceRenderer<String>("toString"), 5, false) {};
    
    // Never mutates the model list after initialization
    // Does not catch the bug where choices list reference changes
    assertNotNull(palette);
}
```