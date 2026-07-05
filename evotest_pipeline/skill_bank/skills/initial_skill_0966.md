---
name: reverse-lexicoder-sort-order-validation
description: When testing a ReverseLexicoder that wraps another lexicoder, verify
  that the decoded-and-reversed sort order is the inverse of the original lexicoder's
  sort order — test with multiple data points including edge cases like dates across
  large time ranges.
code_tags:
- SORT_ORDER_REVERSAL
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# reverse-lexicoder-sort-order-validation

## Instructions

# Reverse Lexicoder Sort Order Validation

## Instructions

- WHEN the TG encounters a `ReverseLexicoder<T>` that wraps another lexicoder (e.g., `ReverseLexicoder<Date>` wrapping `DateLexicoder`, or `ReverseLexicoder<Long>` wrapping `LongLexicoder`)
- THEN it should test that the `ReverseLexicoder`'s `decode(encode(value))` roundtrip preserves each value correctly AND that the **sorted order of the decoded values is the reverse** of the sorted order of the original values
- Specifically, create a list of values in **ascending sort order** (e.g., `[date1920, date2016mid, date2016late]` for `Date` objects, or `[-100, 0, 100]` for integers), encode all of them using `ReverseLexicoder.encode()`, then decode all the byte arrays back, and verify the resulting list is in **reverse sorted order** (e.g., `[date2016late, date2016mid, date1920]`)
- Include values that span the full representable range of the underlying type: for `Date` lexicoders, include dates from year 1920 to the current era; for `Long` lexicoders include negative, zero, and positive values
- Common pitfalls:
  - Testing only one value at a time instead of comparing the relative ordering of multiple values
  - Testing only `encode(decode(...))` roundtrip without checking that sorting order is reversed
  - Using values that are too similar (e.g., same date or same integer) — the test should use values that produce clearly different byte encodings to expose ordering bugs
  - Forgetting that `ReverseLexicoder` must reverse the bytes from the underlying lexicoder — if byte reversal is implemented incorrectly, the decoded values may sort in ascending (original) order instead of descending
- Correct example (for `ReverseLexicoder<Date>` with `DateLexicoder`):
```java
DateLexicoder dateLx = new DateLexicoder();
ReverseLexicoder<Date> rl = new ReverseLexicoder<>(dateLx);
// Dates in ascending order
Date d1 = new Date(-1573263360000L); // 1920
Date d2 = new Date(1469524002000L);  // 2016
Date d3 = new Date(1469524002123L);  // 2016 slightly later
List<Date> ascending = Arrays.asList(d1, d2, d3);
List<Date> descending = Arrays.asList(d3, d2, d1);
// Encode all
List<byte[]> encoded = ascending.stream().map(rl::encode).collect(Collectors.toList());
// Decode all
List<Date> decoded = encoded.stream().map(rl::decode).collect(Collectors.toList());
// Verify reversed order
assertEquals(descending, decoded);
```
- Incorrect example (only roundtrips a single value, misses the ordering check):
```java
DateLexicoder dateLx = new DateLexicoder();
ReverseLexicoder<Date> rl = new ReverseLexicoder<>(dateLx);
Date d = new Date();
assertEquals(d, rl.decode(rl.encode(d))); // This passes even if sort order is wrong!
```