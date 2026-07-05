---
name: ajax-update-component-resolver-chain
description: When a TransparentWebMarkupContainer is nested between a component resolver
  and its target, Ajax responses may resolve to the wrong component by id. This skill
  teaches how to write tests that verify the correct component is rendered in Ajax
  responses by checking the render output for expected vs unexpected marker text.
code_tags:
- VALIDATION
- COMPONENT_RESOLVER_CHAIN
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# ajax-update-component-resolver-chain

## Instructions

# Ajax Update Component Resolver Chain Bug

## Instructions

**WHEN** the TG encounters code that uses `TransparentWebMarkupContainer` (or similar transparent containers) in combination with `IComponentResolver` implementations, AND there are multiple components with the same `wicket:id` at different nesting levels:

- **THEN** the TG should write a test that:
  1. Creates a page with at least two nested containers: a `TransparentWebMarkupContainer` (mc1) containing a child with a specific `wicket:id` (e.g., `"special"`), and a `WebMarkupContainer` (mc2) that breaks the transparent chain, followed by a component-resolving container (mc3) that contains another child with the **same** `wicket:id` (`"special"`).
  2. Adds an AjaxLink or similar Ajax behavior to the page that adds the deeper `"special"` component to the Ajax response target.
  3. Uses a `WebResponse` or `BufferedWebResponse` (or a `StringResponse`) to capture the Ajax response body.
  4. Verifies that the Ajax response contains the expected marker text from the **correct** (deeper) component (e.g., `"CORRECT_SPECIAL"`) and does **NOT** contain the marker text from the **wrong** (shallower, inside the transparent container) component (e.g., `"WRONG_SPECIAL"`).

- **THEN** the TG should target a specific Ajax event (e.g., clicking a link that triggers an Ajax request that adds a component) and capture the rendered response.

- **INCLUDE** concrete test steps:
  - Set up the page with the nested container structure described above.
  - Trigger the Ajax behavior (e.g., by calling `tester.executeAjaxEvent("link", "click")`).
  - Get the last Ajax response from the tester (e.g., via `tester.getLastResponse().getDocument()` or by asserting the response body contains/does not contain specific strings).
  - Assert that the response contains the correct marker text and does not contain the incorrect marker text.

- **COMMON PITFALLS TO AVOID**:
  - ❌ Testing only that the Ajax request succeeds (status 200) without checking the **content** of the response.
  - ❌ Using a simple `WebMarkupContainer` in place of `TransparentWebMarkupContainer` — the transparency is essential to triggering the bug.
  - ❌ Checking only that `"CORRECT_SPECIAL"` is present without also checking that `"WRONG_SPECIAL"` is **absent**.
  - ❌ Placing the correct and wrong components at the same nesting level — the bug requires the wrong one to be inside a transparent container that sits above a component resolver in the hierarchy.
  - ❌ Testing in isolation without the component resolver chain — the bug manifests only when a `IComponentResolver` on the page is resolving components, and a `TransparentWebMarkupContainer` between the resolver and the target causes the resolver to find the wrong component first.

- **CORRECT EXAMPLE**:
```java
// Expected: Ajax response contains "CORRECT_SPECIAL" but NOT "WRONG_SPECIAL"
tester.executeAjaxEvent("link", "click");
String response = tester.getLastResponse().getDocument();
assertThat(response, containsString("CORRECT_SPECIAL"));
assertThat(response, not(containsString("WRONG_SPECIAL")));
```

- **INCORRECT EXAMPLE**:
```java
// WRONG: Only checks status code, not response content
tester.executeAjaxEvent("link", "click");
assertEquals(200, tester.getLastResponse().getStatusCode());
// Missing: verification that the correct component's content is in the response
// Missing: verification that the wrong component's content is NOT in the response
```