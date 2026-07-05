---
name: html-layout-title-configuration
description: When testing HTML layout formatting, verify that the title property is
  correctly applied to the HTML header output, not just the default value. This skill
  teaches how to test layout configuration injection for HtmlLayout.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# html-layout-title-configuration

## Instructions

# HTML Layout Title Configuration Validation

## Instructions

- WHEN the TG encounters a test for `HtmlLayout` (or any layout that generates HTML output with a configurable `<title>` tag)
- THEN it should verify that the configured title value actually appears in the generated output header, not just the default title.
  - The default title is `"Log4j Log Messages"` (stored as `DEFAULT_TITLE` constant in the buggy version).
  - The test should construct a `HtmlLayout` with a custom non-default title (e.g., `"Test Title"`), call `toSerializable()` on a `LogEvent`, and assert that the string output contains `"<title>Test Title</title>"` rather than `"<title>Log4j Log Messages</title>"`.
  - On the buggy version, this assertion will fail because the configured title was not being applied to the header.
- WHEN the TG writes the test, it should also call `getHeader()` on the layout and verify the title appears in the header string.
- Common pitfalls to avoid:
  - Testing ONLY the default title (which works but does not detect the bug)
  - Omitting the `toSerializable()` or `getHeader()` call and only testing layout construction
  - Not using a custom title string that differs from the default
  - Asserting on the full output format without verifying the title tag specifically
- Correct example:
  ```java
  @Test
  public void testCustomTitle() {
      final HtmlLayout layout = HtmlLayout.createDefaultLayout("Test Title");
      final LogEvent event = Log4jLogEvent.newBuilder().build();
      // toSerializable should include the custom title
      assertThat(layout.toSerializable(event)).contains("<title>Test Title</title>");
      // getHeader should also include the custom title
      assertThat(layout.getHeader()).contains("<title>Test Title</title>");
  }
  ```
- Incorrect example (does NOT catch the bug):
  ```java
  @Test
  public void testDefaultTitle() {
      final HtmlLayout layout = HtmlLayout.createDefaultLayout();
      final LogEvent event = Log4jLogEvent.newBuilder().build();
      // Default title works, but does not verify title configuration was applied
      assertThat(layout.toSerializable(event)).contains("<title>Log4j Log Messages</title>");
  }
  ```