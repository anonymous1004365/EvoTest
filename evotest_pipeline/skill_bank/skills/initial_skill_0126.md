---
name: empty-header-value-in-predicate
description: ''
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# empty-header-value-in-predicate

## Instructions

# Empty/Missing Header Value Predicate Test

## Instructions

- WHEN the TG encounters a `ValueBuilder.in(Object...)` call that evaluates a header expression (e.g., `header("xxx").in(...)`)
- AND the test checks that the predicate does NOT match for a header that is absent from the exchange message
- THEN the TG should write a test that:
  1. Creates an `Exchange` via `new DefaultExchange(new DefaultCamelContext())`
  2. Sets up the exchange's `in` message body and a few headers, but deliberately omits the header being tested
  3. Calls `header("xxx").in("Hiram", "Jonathan", "James", "Claus")` to build a predicate
  4. Calls `assertDoesNotMatch(predicate)` or `assertPredicateDoesNotMatch(predicate, exchange)` to verify the predicate returns `false`
  5. Verifies that no `NullPointerException` or other exception is thrown during evaluation

- Common pitfalls to avoid:
  - **Testing only with present headers**: Writing tests that only verify matching behavior when a header exists, without testing the absent/null header case
  - **Assuming non-null header values**: Not testing what happens when `exchange.getIn().getHeader("xxx")` returns `null`
  - **Overlooking the `in()` method logic**: The `header("xxx").in(...)` call creates equality predicates comparing the header value against each provided value, and if the header is null, each comparison should safely return `false` rather than throwing an NPE

## Example

```java
// Correct test for empty/missing header in predicate
public void testEmptyHeaderValueIn() throws Exception {
    // there is no header with xxx
    assertDoesNotMatch(header("xxx").in("Hiram", "Jonathan", "James", "Claus"));
}

// INCORRECT — only tests with existing headers, misses the null/empty case
public void testEmptyHeaderValueIn() throws Exception {
    // Wrong: setting up the header first instead of testing when it's absent
    exchange.getIn().setHeader("xxx", "Hiram");
    assertMatches(header("xxx").in("Hiram", "Jonathan", "James", "Claus"));
}
```