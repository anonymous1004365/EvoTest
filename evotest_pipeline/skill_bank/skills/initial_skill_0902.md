---
name: attribute-modifier-state-preservation-on-append
description: When testing AttributeModifier with append/prepend operations, verify
  that the attribute value state is correctly preserved and not overwritten by null
  or unexpected values. This skill applies to Wicket component attribute modifiers
  that mutate attribute state.
code_tags:
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# attribute-modifier-state-preservation-on-append

## Instructions

# Attribute Modifier State Preservation on Append/Prepend

## Instructions

- WHEN the TG encounters an `AttributeModifier` that uses append/prepend semantics (e.g., `AttributeModifier.append(...)`, `AttributeModifier.prepend(...)`, or custom `newValue()` implementations that concatenate values)
- THEN it should test that after applying the modifier, the attribute value correctly contains both the original value and the appended/prepended value, and that no unexpected `null` value overwrites the accumulated state
- Specifically, verify that when `newValue()` is called with a non-null `currentValue` (the existing attribute value) and a non-null `replacementValue` (the value to append), the returned string is the concatenation of the two, not just the replacement value or a null
- Create a component with an initial attribute value (e.g., `class="foo"`), apply the `AttributeModifier` with a `ReplaceString` behavior (or `AppendingString`) that appends, and assert the final attribute value equals the expected combined string (e.g., `"foo bar"`)
- Common pitfalls to avoid:
  - Testing only the replacement value without ensuring the current value is preserved in the output
  - Forgetting that `newValue()` can return `null` when the replacement value is null, which should NOT overwrite the existing attribute value — the modifier must skip null returns
  - Assuming `newValue()` is called only once — test scenarios where the modifier is applied multiple times with sequential appends
  - Not testing the case where `currentValue` is null (first-time application) separately from the case where `currentValue` is non-null (subsequent applications)

### Correct example (what the TG should write):
```java
// Test that appending preserves existing attribute value
Component component = new Label("id", "text");
component.add(AttributeModifier.append("class", "bar"));
component.add(AttributeModifier.append("class", "baz"));
// After two appends, class should be "bar baz"
assertEquals("bar baz", component.getAttribute("class"));
```

### Incorrect example (what the TG should avoid):
```java
// BAD: Only tests that the replacement value appears, not that previous state is preserved
Component component = new Label("id", "text");
component.add(AttributeModifier.append("class", "bar"));
// This only checks that "bar" is present, but doesn't verify multi-step accumulation
assertTrue(component.getAttribute("class").contains("bar"));
```