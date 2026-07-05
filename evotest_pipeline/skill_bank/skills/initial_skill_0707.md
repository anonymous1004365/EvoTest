---
name: reusable-parameterized-message-throwable-extraction
description: When a reusable message class extracts throwables from parameter arrays
  by checking if the last parameter is a Throwable, the TG should test that throwable
  extraction correctly handles non-throwable parameters that appear before the Throwable,
  and that the throwable type captured is preserved without being overwritten by earlier
  parameters.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# reusable-parameterized-message-throwable-extraction

## Instructions

# Reusable Parameterized Message Throwable Extraction

## Instructions

- WHEN the TG encounters a `ReusableParameterizedMessage` (or similar reusable parameterized message class) that:
  1. Maintains internal mutable state for a cached `Throwable` field (e.g., `throwable`)
  2. Extracts a `Throwable` from the variable-length parameter array by checking if the **last** parameter is a `Throwable`
  3. Processes parameter array elements in a loop and may call `initThrowable(...)` or similar methods that overwrite the internal `throwable` state
  4. Has methods like `setMessageFormat(String, Object[])` or `setFormattedMessage(String)` that reset state but do NOT clear the cached `throwable` when called with no throwable parameters

- THEN the TG should write a **state test** that verifies:
  1. When a `Throwable` is passed as the **last** parameter (e.g., `new Object[]{"msg", new IllegalAccessError("#1")}`), the message correctly captures **that specific** `Throwable` type and message.
  2. When the message object is **reused** (via `setMessageFormat` or similar) with a **different** `Throwable` as the last parameter (e.g., `new Object[]{"msg", new UnsupportedOperationException("#2")}`), the captured throwable **must be updated to the new type** (e.g., `UnsupportedOperationException`), not retain the old type.
  3. When a `Throwable` is **not** the last parameter (e.g., a `Throwable` at index 0 followed by a `String` at index 1), the throwable should NOT be set (i.e., the internal throwable state should remain `null` or whatever the "no throwable" sentinel is).
  4. Call `getThrowable()` after each call to `setMessageFormat(...)`/`setFormattedMessage(...)` to assert the exact throwable type, message, and null-ness.

- Concrete example of what the test should verify:
  - Create a `ReusableParameterizedMessage` instance.
  - Call `setMessageFormat("{}", new Object[]{"test", new IllegalAccessError("#1")})`.
  - Assert `getThrowable()` is an `IllegalAccessError` with message `"#1"`.
  - Call `setMessageFormat("{}", new Object[]{"test", new UnsupportedOperationException("#2")})`.
  - Assert `getThrowable()` is an `UnsupportedOperationException` with message `"#2"`, NOT `IllegalAccessError`.

- Common pitfalls to avoid:
  - Testing **only** that the throwable is non-null — the test must verify the **exact type and message** of the throwable, not just its presence.
  - Creating a **new** message instance for each test case — the whole point is that `ReusableParameterizedMessage` is **reused**; the TG must make multiple calls on the **same** instance.
  - Forgetting to test the case where no `Throwable` parameter exists (e.g., `new Object[]{"a", "b"}`) — the throwable should be cleared/null after such a call.
  - Testing with only one type of `Throwable` (e.g., only `RuntimeException`) — use **different** `Throwable` subtypes (e.g., `IllegalAccessError` then `UnsupportedOperationException`) to ensure type information is preserved/correctly updated.
  - Not calling `getThrowable()` between reuse calls — the internal state may be stale from the previous call.