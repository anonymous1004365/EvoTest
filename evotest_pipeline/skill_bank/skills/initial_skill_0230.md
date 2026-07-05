---
name: validator-property-resource-resolution
description: When writing tests for FormComponent validation error message resolution,
  test that the property resource lookup correctly falls back through multiple key
  formats (componentId.prefix.key, componentId.key, prefix.key, key) without throwing
  MissingResourceException. This skill applies to Wicket's FormComponent.MessageSource
  and similar resource-bundle-based message resolution chains.
code_tags:
- ARGUMENT_VALIDATION
- EDGE_CASE_INPUT
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# validator-property-resource-resolution

## Instructions

# Validator Property Resource Resolution

## Instructions

- WHEN the test involves validation error messages being resolved through Wicket's `FormComponent.MessageSource` (which chains through keys like `componentId.prefix.key`, `componentId.key`, `prefix.key`, `key`), and the component has a `validatorKeyPrefix` configured on its form
- THEN the test MUST verify that the message resolution process correctly falls back through all four key formats in order, and specifically MUST test that when `validatorKeyPrefix` is set, the `[componentId].[key]` format (without prefix) is still tried correctly — the bug was that when a prefix exists, the lookup of `[componentId].[key]` (without prefix) was skipped, causing a later `MissingResourceException` on the `[key]`-only lookup when the `[prefix].[key]` resource was present but the fallback wasn't
- The test should call `validateRequired()` on the FormComponent, then verify the actual error message text via `getFeedbackMessages().iterator().next().getMessage().toString()`, asserting exact string content that confirms the correct resource was resolved
- Include tests in multiple locales (e.g., `Locale.ENGLISH` and `new Locale("nl")`) to verify that locale-specific properties files are correctly resolved
- Common pitfall: Testing only the happy path where all resource keys are present; the bug manifests when `[componentId].[key]` (without prefix) is NOT present but `[prefix].[key]` IS present, causing the prefix to be incorrectly stripped from subsequent fallback lookups. Also, avoid testing validation messages by just checking that an error exists — you MUST assert the exact message string content.

**Correct example (testing fallback chain with prefix):**
```java
// When form has getValidatorKeyPrefix() returning "myPrefix", and TestForm.properties 
// contains "myPrefix.Required=Custom: {0} is required" and "textField.Required=Specific: {0} is required"
textField.setInput("");
textField.validateRequired();
String msg = textField.getFeedbackMessages().iterator().next().getMessage().toString();
// Should be "Specific: textField is required" (finds componentId.key before prefix.key)
assertEquals("Specific: textField is required", msg);
```

**Incorrect example (not testing the resolution chain at all):**
```java
// WRONG: Just checks that an error exists without asserting exact message content
textField.setInput("");
textField.validateRequired();
assertTrue(textField.getFeedbackMessages().hasError()); // Doesn't verify what message was resolved
```

- Common pitfall: Not testing the caching behavior of the message source — the `triedKeys` set is only populated per component instance, and messages are cached; repeat the same assertion twice to verify caching doesn't break resolution.
- Common pitfall: Not testing locale switching — after testing with one locale, create a new page instance, set a different locale (e.g., `tester.getSession().setLocale(new Locale("nl"))`), and re-run the validation/assertions to verify locale-specific `.properties` files work.