---
name: session-attribute-page-not-rendered
description: When a redirect (RestartResponseException, setResponsePage) replaces
  the current page but the new target page has not been fully rendered before the
  session is stored, the session may contain incomplete state. Tests should verify
  that session attributes set by the final rendered page are present after the redirect
  chain.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# session-attribute-page-not-rendered

## Instructions

# Session Attribute Persistence After Redirect Without Rendering

## Instructions

- WHEN the TG encounters code where a `RestartResponseException` or `setResponsePage()` redirects to another page, and the source code sets/removes session attributes (via `getSession().setAttribute(...)` / `getSession().removeAttribute(...)`) or the final page stores state in session attributes
- THEN the TG should write a test that:
  1. Starts at a page that performs a redirect (either via `RestartResponseException` or `setResponsePage()`)
  2. Follows the redirect programmatically (e.g., by calling `tester.startPage(initialPage)` which automatically follows redirects)
  3. After the redirect completes, verifies that the session attributes set by the **final rendered page** exist with the expected values
  4. **Concrete example**: If PageA throws `RestartResponseException(PageC.class)` in its constructor and PageC sets a session attribute like `getSession().setAttribute("testAttribute", "testValue")`, verify with `tester.getSession().getAttribute("testAttribute")` that the attribute is present and equals the expected value — not null
  
- **Common pitfalls to avoid**:
  - ❌ Testing only that the redirect mechanism itself works (e.g., only checking HTTP status codes or page class after redirect) without verifying that session state is correctly preserved
  - ❌ Writing a test that sets the session attribute before the redirect and checks it, instead of having the final page set the attribute during its own rendering
  - ❌ Assuming that because the redirect targets a page that sets session attributes, those attributes will always persist — this is the exact bug pattern (when the page causing the redirect is not rendered, session state set later may not be stored)
  - ❌ Not explicitly checking for specific attribute values with getAttribute(); instead just checking that the attribute map is non-null

- **Correct test pattern**:
```java
// PageC sets session attribute in its constructor
tester.startPage(PageA.class); // PageA redirects to PageC via RestartResponseException
Assert.assertEquals("testValue", tester.getSession().getAttribute("testAttribute"));
```

- **Incorrect test pattern**:
```java
// Only checks that the right page class is rendered, without session state verification
tester.startPage(PageA.class);
Assert.assertEquals(PageC.class, tester.getLastRenderedPage().getClass());
```