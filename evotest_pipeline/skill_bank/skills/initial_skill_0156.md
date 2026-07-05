---
name: locale-change-clear-cache
description: When testing components that cache localized resource strings, the TG
  should verify that changing the session locale triggers cache invalidation and the
  new locale's values are picked up. This skill helps catch bugs where resource string
  caches (e.g., in ResourceModel, StringResourceModel) are not cleared when the session
  locale changes.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# locale-change-clear-cache

## Instructions

# Locale Change Cache Invalidation

## Instructions

- WHEN the TG encounters a model/cache that stores localized resource strings (e.g., `ResourceModel`, `StringResourceModel`, or any custom model that calls `Localizer.getString()` and caches the result)
- THEN the TG should write a test that:
  1. Sets the session to locale A (e.g., `Locale.GERMAN`)
  2. Renders a component/page that triggers the model to obtain a resource string for locale A
  3. Asserts the model returns the expected string for locale A (e.g., `"label from properties DE"`)
  4. Calls `page.detach()` to simulate page detachment (clearing detachable model cache)
  5. Changes the session locale to locale B (e.g., `Locale.FRENCH`)
  6. Re-renders the same page or re-reads the same model (e.g., calls `tester.startPage(page)`)
  7. Asserts the model now returns the expected string for locale B (e.g., `"label from properties FR"`)

- The test should use **two different locales** (e.g., `Locale.GERMAN` and `Locale.FRENCH`) and verify that after changing the locale, the string is NOT stale. The failure will manifest as the cached value from locale A being returned instead of the correct value for locale B.

- **Common pitfalls:**
  - ❌ Testing only one locale — this does not detect caching bugs that cause stale values after locale switches.
  - ❌ Forgetting to detach the page before re-rendering — without `page.detach()`, the model may still hold a reference to the old page/component, and the fix may not be exercised.
  - ❌ Creating a new page instance for locale B instead of re-rendering the same page — the bug is about an existing page's model cache not being invalidated; using a fresh page may bypass the caching logic entirely.
  - ❌ Assuming `ResourceModel` is stateless — it caches its result internally; locale changes must trigger cache invalidation.

- **Correct example (from `AutoFormLabelPickupTest.testLocaleChangesAreDetectedWithExplicitMessageKeys`):**
  ```java
  @Test
  public void localeChangesAreDetectedWithExplicitMessageKeys() throws Exception
  {
      Session.get().setLocale(Locale.GERMAN);
      tester.startPage(new PickUpLabelPage(null));
      assertEquals(
          "label from properties DE",
          ((FormComponent)tester.getComponentFromLastRenderedPage("form:inputPropertiesLabel")).getLabel()
              .getObject());

      Session.get().setLocale(Locale.FRENCH); // change locale
      Page page = tester.getLastRenderedPage();
      page.detach(); // ensure model cache is cleared
      tester.startPage(page); // re-render same page instance
      assertEquals(
          "label from properties FR",
          ((FormComponent)tester.getComponentFromLastRenderedPage("form:inputPropertiesLabel")).getLabel()
              .getObject());
  }
  ```

- **Incorrect example (test that would NOT catch the bug):**
  ```java
  @Test
  public void localeChangesNotDetected() throws Exception
  {
      Session.get().setLocale(Locale.GERMAN);
      tester.startPage(new PickUpLabelPage(null));
      assertEquals("DE", getLabelValue());

      Session.get().setLocale(Locale.FRENCH);
      // Missing: page.detach()
      // Missing: re-rendering the same page
      // Just checks something unrelated
      assertEquals("FR", getLabelValueFromNewPage()); // new page — may not exercise cache
  }
  ```