---
name: page-provider-type-identity-check
description: When resolving a page by its identifier, test that the returned page's
  class matches the expected type. This skill prevents the bug where a stale page
  is returned even though its class differs from what the caller requested.
code_tags:
- NULL_CHECK
- TYPE_CHECK
- STATE_CHECK
test_pattern: STATE_TEST
---

# page-provider-type-identity-check

## Instructions

# Page-Provider Type Identity Check

## Instructions

- WHEN the TG encounters code that resolves a page/component by its identifier and the identifier can be stale (e.g., a page stored from a previous request), AND the resolution logic explicitly checks the class of the found page against the expected page class
- THEN the TG MUST write a test that:
  1. Creates a page of one type (e.g., `MockPageWithLink`) and stores it so that its identifier is remembered
  2. Creates or registers a *different* page class (e.g., a local `TestPage`) with the **same** identifier
  3. Requests the page from the provider, explicitly setting the expected page class to the first type
  4. Asserts that the returned page **throws an exception** (e.g., `IllegalArgumentException` or similar) or is `null`, because its actual class does not match the expected class

- **What to verify**: The test must verify that the provider does NOT return a page whose runtime type differs from the requested type, even if the page ID matches. The failure on the buggy version will be a `ComparisonFailure` complaining that the actual class (e.g., `TestPage`) does not equal the expected class (e.g., `MockPageWithLink`).

- **Common pitfalls to avoid**:
  - ❌ Testing only with identical page types — this misses the type-mismatch scenario
  - ❌ Not ensuring the identifier for the stale page is the same as the new page's identifier
  - ❌ Assuming the provider will always return `null` when a mismatch occurs; the buggy version returns the wrong page
  - ❌ Forgetting to set both the constructor-provided class and the page identifier when constructing the provider

- **Correct example** (Java):
  ```java
  @Test
  public void ignorePageFoundByIdIfItsClassDoesntMatch() {
      // Store a page of type MockPageWithLink
      MockPageWithLink old = new MockPageWithLink();
      old.setId(123);
      // ... store old page in the page store so that id 123 points to MockPageWithLink

      // Register a NEW page with same id but DIFFERENT class
      TestPage newPage = new TestPage();
      newPage.setId(123);
      // ... make the page store map id 123 to TestPage now

      PageProvider provider = new PageProvider(MockPageWithLink.class, new PageParameters(), 123);
      PageProviderTest.verifyIllegalArgException(provider);
  }
  ```

- **Incorrect example** (too weak, doesn't catch the bug):
  ```java
  @Test
  public void testPageFoundById() {
      MockPageWithLink page = new MockPageWithLink();
      page.setId(123);
      // ... store page
      
      // Only tests the happy-path where types match
      PageProvider provider = new PageProvider(MockPageWithLink.class, new PageParameters(), 123);
      IPageSource source = ...;
      assertNotNull(provider.getPageSource());
  }
  ```