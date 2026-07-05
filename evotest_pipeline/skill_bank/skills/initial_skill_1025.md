---
name: inline-enclosure-attribute-backup-restore
description: When InlineEnclosure containers receive generated markup attributes (like
  wicket:name) during rendering, the test should verify that attribute values are
  properly restored to their original state after enclosures are closed. This is critical
  for Ajax updates where placeholder tags must carry correct attributes.
code_tags:
- AJAX_INLINECLOSURE_PLACEHOLDER
test_pattern: STATE_TEST
---

# inline-enclosure-attribute-backup-restore

## Instructions

# InlineEnclosure Markup Attribute Restoration

## Instructions

- WHEN the TG encounters an `InlineEnclosure` component that manages child component visibility through markup containers (enclosures):
  - THEN the TG should write a test that renders a page containing an `InlineEnclosure`, verifies the generated markup, and checks that attribute values (such as `id` attributes containing wicket-generated names) are correctly restored/propagated to the container tag after the enclosure closes.
  - The test should use `tester.startPage(...)` and `tester.assertResultPage(...)` with a specific expected HTML file/resource to compare against.
  - The test must verify that numeric suffix values in `id` attributes (e.g., `id="automInlineEnclosureId7"`) match expected values rather than being empty or missing (e.g., `id="automInlineEnclosureId"`).
  - Include at least one assertion that the rendered HTML contains the correct attribute value, not just the presence of the attribute.

- WHEN the TG writes tests to reproduce bugs in `InlineEnclosure` or `Enclosure` classes:
  - THEN the TG must ensure the test renders a full page (not just a component fragment), because the enclosure's behavior depends on the markup hierarchy and wicket:id resolution during render.
  - The test should compare the full rendered output against a stably versioned expected result file to catch regressions in attribute propagation.

- Common pitfalls to avoid:
  - Testing only the presence/absence of child components inside enclosures without checking the enclosing tag's attributes.
  - Using `tester.assertContains(...)` which is too loose — instead use `tester.assertResultPage(...)` with a strict expected file.
  - Assuming that wicket:name/id attribute values are deterministic across renders without verifying their numeric suffixes.
  - Testing only the non-Ajax (full-page render) case without also checking Ajax update scenarios where the placeholder container is re-rendered.

### Correct Example (what the test should do):
```java
// Test that InlineEnclosure correctly restores wicket:id attribute after enclosure
tester.startPage(new InlineEnclosurePage_1());
tester.assertResultPage(InlineEnclosurePage_1.class, "InlineEnclosurePageExpectedResult_1.html");
```

### Incorrect Example (what to avoid):
```java
// WRONG: Only checks component presence, missing attribute restoration
tester.startPage(new InlineEnclosurePage_1());
assertNotNull(tester.getComponentFromLastRenderedPage("someChild"));
// No assertion on the container tag's wicket:id attribute value
```