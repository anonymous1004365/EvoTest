---
name: safe-copy-behavior
description: When a class implements a `copy(boolean safeCopy)` method where `safeCopy=true`
  should produce a defensive copy but the buggy version has `getIn()` returning null
  or fails to initialize the message, test that the safe copy produces a proper Exchange
  with non-null In message, headers, and that modifications to the copy do not affect
  the original.
code_tags:
- VALIDATION
- NULL_CHECK
- EXCEPTION_HANDLING
- SAFE_COPY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# safe-copy-behavior

## Instructions

# Safe Copy Behavior

## Instructions

- WHEN the TG encounters a `copy(boolean safeCopy)` method on an `Exchange` (e.g., `DefaultExchange.copy(boolean safeCopy)`) that conditionally initializes `exchange.getIn()` and copies headers/properties via helper methods like `safeCopyHeaders(Map)` or `safeCopyProperties(Map)`
- THEN the TG should write a test that:
  1. Creates an Exchange with at least one header (e.g., `"foo" -> "bar"`) and at least one property (e.g., `"myProp" -> "myValue"`)
  2. Calls `exchange.copy(true)` to perform a safe copy
  3. Verifies the **original** exchange still has the original headers and properties after the copy
  4. Verifies the **copy** has the same headers and properties
  5. Modifies a header in the copy (e.g., `copy.getIn().getHeaders().put("foo", "changed")`) and verifies the original exchange's headers are **not** affected (i.e., the maps are distinct objects)
  6. Verifies the copy's In message is non-null (`assertNotNull(copy.getIn())`)

- Key pitfalls to avoid:
  - **DO NOT** assume `getIn()` returns a non-null message in the safe-copy path before headers are set. In the buggy version, `exchange.copy(true)` calls `exchange.getIn()` on the *new* exchange which may return `null` if no In message was initialized, causing a `NullPointerException`.
  - **DO** ensure the original exchange has an In message with headers set before calling `copy(true)`. The `DefaultExchange` constructor may not create an In message; call `exchange.getIn().setBody(...)` or access the In message to trigger lazy initialization before proceeding.
  - **DO** test both with and without headers/properties. If `getIn().hasHeaders()` returns false, the headers are not copied — verify this edge case.
  - **DO NOT** confuse `copy()` with `copy(true)` — the default copy (`copy(false)`) uses `getIn().copy()` which is a different code path and may not expose this bug.

### Correct example (fixed behavior):
```java
DefaultExchange exchange = new DefaultExchange(context);
exchange.getIn().setBody("hello");
exchange.getIn().setHeader("foo", "bar");
exchange.setProperty("myProp", "myValue");

Exchange copy = exchange.copy(true);

assertNotNull(copy.getIn());
assertEquals("hello", copy.getIn().getBody());
assertEquals("bar", copy.getIn().getHeader("foo", String.class));
assertEquals("myValue", copy.getProperty("myProp", String.class));

// Verify defensive copy: modifying copy doesn't affect original
copy.getIn().getHeaders().put("foo", "changed");
assertEquals("bar", exchange.getIn().getHeader("foo", String.class));
```

### Incorrect example (misses the bug):
```java
// This fails on the buggy version because copy(true) calls exchange.getIn()
// on the new exchange, which returns null if getIn() hasn't been initialized.
DefaultExchange exchange = new DefaultExchange(context);
exchange.setProperty("myProp", "myValue");
Exchange copy = exchange.copy(true);  // NullPointerException on buggy version
```

### What the test should detect:
- On the **buggy** version, `exchange.copy(true)` may throw a `NullPointerException` because `exchange.getIn()` returns `null` on the new `DefaultExchange(this)` before any headers or body are set. The fix ensures the In message is properly initialized before accessing it in the safe-copy path.
- Even if no NPE occurs, the test should verify that the original's headers are not mutated by changes to the copy's headers (defensive copy semantics).