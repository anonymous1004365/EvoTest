---
name: null-message-filter-returns-onmismatch
description: When a filter overrides multiple filter() overloads from AbstractFilter,
  the test must cover each overload with null message arguments (Object, Message,
  String) to verify consistent null-safe behavior. This skill catches cases where
  some overloads handle null but others throw NullPointerException.
code_tags:
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# null-message-filter-returns-onmismatch

## Instructions

# Null Message Filter Returns onMismatch

## Instructions

- WHEN the TG encounters a custom Filter class that extends `AbstractFilter` and overrides multiple `filter(...)` method overloads (such as `filter(Logger, Level, Marker, Object, Throwable)`, `filter(Logger, Level, Marker, Message, Throwable)`, and `filter(Logger, Level, Marker, String, Object...)`)
- THEN the TG should test ALL overridden filter methods by passing `null` as the message argument (the 4th parameter), verifying that each overload returns `Result.onMismatch` (typically `Result.DENY`) instead of throwing a `NullPointerException`
- Include the specific overload signatures in assertions — e.g., `assertSame(Result.DENY, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null))` tests the `Object msg` overload, while `assertSame(Result.DENY, filter.filter(null, Level.DEBUG, null, (Message) null, (Throwable) null))` tests the `Message msg` overload
- For the `String msg` varargs overload, test with `filter(null, Level.DEBUG, null, null, (Object[]) null)` to pass a null String message with null varargs
- Common pitfall: Testing only one filter overload (e.g., only the `Object msg` variant) and missing that a different overload (e.g., `Message msg` or `String msg`) fails on null
- Common pitfall: Not using explicit casts like `(Object) null` and `(Message) null` to disambiguate which overload is being called
- Common pitfall: Assuming the base class `AbstractFilter` handles null in all overloads — subclasses may override only some overloads and forget null checks in others

### Correct example (in JUnit):
```java
@Test
public void testNullMessageReturnsOnMismatch() {
    RegexFilter filter = RegexFilter.createFilter(".* test .*", null, false, null, null);
    filter.start();
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, (Message) null, (Throwable) null));
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, null, (Object[]) null));
}
```

### Incorrect example (missed overloads):
```java
@Test
public void testNullMessageReturnsOnMismatch() {
    RegexFilter filter = RegexFilter.createFilter(".* test .*", null, false, null, null);
    filter.start();
    // Only tests Object msg overload — Missing Message and String overloads!
    assertSame(Filter.Result.DENY, filter.filter(null, Level.DEBUG, null, (Object) null, (Throwable) null));
}
```