---
name: page-instance-availability-reporting
description: When a handler resolves a page lazily (from a class link), it must not
  report a page instance as available before the handler is actually invoked. This
  skill teaches how to test that isPageInstanceAvailable() correctly returns false
  when the page is created from a class rather than provided as an existing instance.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- STATE_MUTATION
- PAGE_INSTANCE_LIFECYCLE
test_pattern: STATE_TEST
---

# page-instance-availability-reporting

## Instructions

# Page Instance Availability Reporting

## Instructions

- WHEN the TG encounters a request handler that can resolve a page from either a **page class** (e.g., `PageProvider` or `PageAndComponentProvider` with a `Class<? extends Page>`) or a **page instance** (e.g., `PageProvider` with an existing `Page` object)
- THEN the TG should write a test that:
  1. Creates the handler using a **page class** (e.g., `new PageProvider(MyPageClass.class, null)` or `new PageAndComponentProvider(MyPageClass.class, component, interfaceClass)`) — NOT a concrete page instance
  2. Invokes `isPageInstanceAvailable()` (or a similar method that reports page instance availability) **before** `getPage()` or any other method that triggers page instantiation
  3. Asserts that `isPageInstanceAvailable()` returns **`false`** — because when the page is only known by class, a page instance has not yet been created and should not be reported as available
  4. Invokes `getPage()` to trigger lazy instantiation
  5. Optionally asserts that `isPageInstanceAvailable()` now returns `true` after the page was created

- The test must verify that the handler **does not eagerly create** a page instance just to check availability. The bug occurs when the handler's `isPageInstanceAvailable()` implementation incorrectly triggers page creation (e.g., by calling `getPage()` internally) and thus reports that a page instance is always available, even for class-based links.

- **Common pitfalls to avoid:**
  - ❌ Testing only with a page **instance** (e.g., `new PageProvider(page)`) — this will trivially return `true` for `isPageInstanceAvailable()`, missing the bug
  - ❌ Calling `getPage()` before checking `isPageInstanceAvailable()` — this forces lazy instantiation and defeats the purpose of the check
  - ❌ Assuming that a class-based page provider can never produce a page (it can — just lazily) — the distinction is about *when* the instance is created, not *whether* it can be created
  - ❌ Not testing the specific handler class (e.g., `ListenerRequestHandler`) — the bug may affect a particular handler subclass, not just the generic page provider

- **Correct approach example:**
  ```java
  // Create handler from page class (not instance)
  PageAndComponentProvider provider = new PageAndComponentProvider(
      TestPage.class, component, ListenerInterface.class);
  ListenerRequestHandler handler = new ListenerRequestHandler(provider);

  // BEFORE calling getPage(), check availability
  assertFalse("Handler should not report a page instance is available for class-based links",
      handler.isPageInstanceAvailable());

  // Now trigger lazy creation
  Page page = handler.getPage();
  assertNotNull("Page should be created", page);
  ```

- **Incorrect approach example:**
  ```java
  // BAD: Uses page instance directly
  PageAndComponentProvider provider = new PageAndComponentProvider(
      page, component, ListenerInterface.class);
  ListenerRequestHandler handler = new ListenerRequestHandler(provider);

  // BAD: This test will always pass because the page was already provided
  assertTrue(handler.isPageInstanceAvailable());
  ```