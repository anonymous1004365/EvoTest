---
name: radio-group-persistent-selection-on-re-render
description: When rendering a RadioGroup or similar selection component that tracks
  removed children, the component must maintain persistent selections across re-renders.
  Tests should verify that already-selected values remain selected after removal of
  unselected children and subsequent re-rendering.
code_tags:
- COMPONENT_TREE_NAVIGATION
- CHILD_REMOVAL
- STATE_MUTATION
test_pattern: STATE_TEST
---

# radio-group-persistent-selection-on-re-render

## Instructions

# RadioGroup Persistent Selection on Re-render

## Instructions

- WHEN the TG encounters a `RadioGroup<V>` or similar FormComponent that delegates rendering to child components (like `Radio`) and internally tracks which children were removed using a `Set<String>`
- THEN the TG should write a test that:
  1. Creates a `RadioGroup` and adds multiple `Radio` children bound to different values
  2. Sets the model object of the RadioGroup to a value corresponding to one of the Radios (e.g., `group.setModelObject("selectedValue")`)
  3. Removes one or more *unselected* Radio children from the group (e.g., `group.remove(radioWithUnselectedValue)`)
  4. Calls `group.renderHead(component, response)` (or the equivalent rendering method) and asserts that the selected value is still correctly reflected in the rendered output
  5. Specifically verifies that the selection state is preserved even though some unrelated children were removed after the selection was made
- The TG MUST verify that the internal `Set<String>` used to track removed children does NOT include the value associated with the selected child, otherwise the selection will be lost on re-render
- Common pitfalls: testing only rendering without removal, or testing removal without checking that selection persists; testing only the initial render without a subsequent re-render after child removal; assuming that selection state is re-computed each render rather than stored persistently

- Correct example (in spirit):
  ```java
  RadioGroup<String> group = new RadioGroup<>("group", Model.of("B"));
  Radio<String> radioA = new Radio<>("a", Model.of("A"));
  Radio<String> radioB = new Radio<>("b", Model.of("B"));
  group.add(radioA);
  group.add(radioB);
  // Render — selection "B" is established
  group.remove(radioA); // remove unselected child
  // Re-render — expect selection "B" to still be present
  ```

- Incorrect example:
  ```java
  RadioGroup<String> group = new RadioGroup<>("group", Model.of("B"));
  Radio<String> radioA = new Radio<>("a", Model.of("A"));
  Radio<String> radioB = new Radio<>("b", Model.of("B"));
  group.add(radioA);
  group.add(radioB);
  group.remove(radioB); // removing the selected child — wrong test scenario
  // This doesn't test the bug: the bug is about removing unselected children
  ```