---
name: rtl-page-overflow-transform-validation
description: When testing right-to-left (RTL) page overflow behavior combined with
  CSS transforms (e.g., translateX), verify that transformed content does not cause
  extra blank pages or incorrect pagination. The TG should specifically test RTL text
  with overflow and transform properties.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- VALIDATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# rtl-page-overflow-transform-validation

## Instructions

# RTL Page Overflow with Transform Validation

## Instructions

**WHEN** the TG encounters code that handles right-to-left (RTL) page layout, page overflow behavior, or CSS transforms (especially `translateX` or similar translation transforms) in a paginated rendering context (e.g., HTML to PDF conversion):

- **THEN** the TG should write a test that combines RTL text with overflow content AND a CSS transform (e.g., `transform: translateX(...)`) to verify that no extra blank pages are produced.
- **THEN** the test should verify the total number of pages/output items — specifically, ensure that the RTL + transform + overflow combination produces the same number of pages as without the transform, or a clearly expected number.
- **THEN** the test should check that no unexpected blank pages are introduced at the end of the document (i.e., the last page contains meaningful content, not just whitespace/emptiness).
- **THEN** include test variants: (1) RTL + overflow without transform (baseline), (2) RTL + overflow WITH a `translateX` transform, and (3) if applicable, LTR equivalent for comparison.

**Common pitfalls to avoid:**
- ❌ Testing only LTR (left-to-right) text and assuming RTL behavior is identical.
- ❌ Testing transforms in isolation without overflow/ pagination context.
- ❌ Only checking for exceptions/errors — visual page count and blank-page detection is critical here.
- ❌ Assuming that document body-level transforms in RTL don't affect page overflow calculation.
- ❌ Using a single page of content when the bug only manifests with multi-page overflow scenarios.

**Correct example (pattern):**
```java
// Given an RTL HTML template with enough text to overflow a single page,
// plus a translateX transform on the body:
String html = "<html><body style=\"direction: rtl; transform: translateX(50px); font-size: 20px;\">"
    + repeat("some text ", 500)
    + "</body></html>";

// When converting to PDF with A4 page size:
byte[] pdf = render(html, PageSize.A4);

// Then verify page count is not inflated by blank pages:
assertThat(getPageCount(pdf)).isEqualTo(expectedPageCount);
// Also verify last page is non-empty (visual check or text extraction).
```

**Incorrect example (would miss the bug):**
```java
// Only tests LTR with transform — does not trigger the RTL-specific bug:
String html = "<html><body style=\"transform: translateX(50px);\">..."
// Only tests RTL without transform — does not trigger the overflow + transform interaction:
String html = "<html><body style=\"direction: rtl;\">..."
// Only checks that no exception is thrown (no page count assertion):
render(html); // silently produces extra blank pages
```