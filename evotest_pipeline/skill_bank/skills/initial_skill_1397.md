---
name: detect-markup-body-inside-head-recursion
description: Detect StackOverflowError caused by infinite recursion when HTML markup
  has <body> inside <head>, where the parser's error handling should throw MarkupException
  but instead causes infinite recursion. Apply when testing markup parsing/validation
  for malformed HTML structures.
code_tags:
- RECURSIVE_INFINITE_LOOP
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# detect-markup-body-inside-head-recursion

## Instructions

# Detect StackOverflowError Instead of Expected MarkupException in Malformed Markup

## Instructions

- WHEN the TG encounters a markup parser or filter (e.g., `HtmlHeaderSectionHandler`) that validates the structure of HTML tags (like `<head>` and `<body>`) AND the code is supposed to detect invalid nesting (e.g., `<body>` found inside unclosed `<head>`) and throw a `MarkupException`,
- THEN the TG should write an EXCEPTION_TEST that:
  1. Creates a markup string with the invalid nesting, e.g., `<html><head><body>bad markup!</body></head></html>` (where `<head>` is not closed before `<body>`)
  2. Feeds this markup into a page/component that uses `IMarkupResourceStreamProvider` returning the malformed markup as a `StringResourceStream`
  3. Expects `MarkupException` with `@Test(expected = MarkupException.class)`
  4. Verifies that the test does NOT produce a `StackOverflowError` — if it does, the fix is missing
  
- WHEN testing markup validation where a condition check (e.g., `if (foundHead && !foundClosingHead)`) is meant to detect invalid structure and throw,
- THEN verify that this condition is reached BEFORE any recursive processing that could cause infinite recursion. If the error-throwing logic is positioned after a recursive call or inside a loop/recursion that processes markup elements, ensure the test detects a `StackOverflowError` vs the expected `MarkupException`.

- Common pitfalls to avoid:
  - ❌ Testing only with valid/correct markup — this won't catch the bug. Always include invalid markup cases.
  - ❌ Assuming the exception-throwing code path is reached — verify by running the test on the buggy version to see if you get `MarkupException` or `StackOverflowError`.
  - ❌ Creating markup that is too simple — use nested tags that trigger the parser's recursive element processing.
  - ❌ Not checking the exact exception type — if the buggy code infinite-loops, you'll get `StackOverflowError` instead of the expected `MarkupException`.

- Correct example (what the test should look like):
  ```java
  @Test(expected = MarkupException.class)
  public void loadMarkupWithBodyInsideHead() throws Exception
  {
      CustomMarkupPage customMarkupPage = new CustomMarkupPage();
      tester.startPage(customMarkupPage);
  }
  
  private static class CustomMarkupPage extends WebPage implements IMarkupResourceStreamProvider
  {
      @Override
      public IResourceStream getMarkupResourceStream(MarkupContainer container,
          Class<?> containerClass)
      {
          // <head> is not closed before <body> — this should throw MarkupException, not StackOverflowError
          return new StringResourceStream("<html><head><body>bad markup!</body></head></html>");
      }
  }
  ```

- ❌ Incorrect pattern (would miss the bug):
  ```java
  @Test(expected = MarkupException.class)
  public void loadMarkupWithBodyInsideHead() throws Exception
  {
      // Only testing with valid markup — won't detect the bug
      tester.startPage(new MyValidPage());
  }
  ```