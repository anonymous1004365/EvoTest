---
name: component-queueing-inside-header-section
description: When testing component queueing with wicket:head sections, the TG should
  verify that queued components inside a header section are correctly resolved and
  rendered. Use this skill when a page or component has wicket:head markup with queued
  children.
code_tags:
- STATE_MUTATION
- COMPONENT_QUEUEING
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# component-queueing-inside-header-section

## Instructions

# Component Queueing Inside Header Sections

## Instructions

- WHEN a `WebPage` or `Panel` has a `<wicket:head>` section in its markup AND components are queued (`queue()`) inside that head section (or using `HeaderSectionMyLabel2` or similar header-participating components)
- THEN create a test that:
  1. Queues a component that participates in header contributions (e.g., `HeaderSectionMyLabel2("label", "mein Label")`) into a page
  2. Starts the page using `tester.startPage(page)`
  3. Asserts that the page renders successfully without "Markup Unable to find component" exceptions
  4. Verifies the queued component's output is present (e.g., `tester.assertContains("mein Label")`)
  
- The key pitfall to avoid: **testing only components queued in the body** and not testing components queued in the `<wicket:head>` section. Components inside `<wicket:head>` are resolved differently because they belong to a header section that is rendered separately from the body. Failing to test this scenario means missing bugs where the queuing mechanism doesn't properly match components inside header markup.

- Concrete example for a bug-capturing test:
  ```java
  // Page with a component that lives inside wicket:head
  public class HeaderSectionPage_11 extends WebPage {
      public HeaderSectionPage_11() {
          add(new HeaderSectionMyLabel2("label", "mein Label"));
      }
  }
  
  @Test
  public void queueInsideHeader() {
      // This test should render the page successfully
      // The bug: queueing inside header sections fails with "Markup Unable to find component"
      HeaderSectionPage_11 page = new HeaderSectionPage_11();
      tester.startPage(page);
      tester.assertContains("mein Label");
  }
  ```

- Common mistake: writing a test that only queues components in the page body (e.g., `<div wicket:id="bodyComponent">`) and assumes the queuing mechanism works identically in all contexts. The header section has a different markup resolution path and must be tested explicitly.