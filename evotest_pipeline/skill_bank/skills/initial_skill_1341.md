---
name: cookie-equality-property-comparison
description: ''
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
- COOKIE_PROPERTY_COMPARISON
- NULL_CHECK
test_pattern: STATE_TEST
---

# cookie-equality-property-comparison

## Instructions

# Cookie Equality Property Comparison

## Instructions

- WHEN the TG encounters a method that compares two `javax.servlet.http.Cookie` objects for equality (e.g. `Cookies.isEqual(c1, c2)` or a `Key.equals(Object)` method that extracts cookie properties like name, path, and domain)
- THEN the TG should write a state-based test that:
  1. Creates two `Cookie` objects with the same `name` and `value` but different `path` values (e.g., `c1.setPath("/app")` vs `c2.setPath("/other")`), and asserts they are **not** equal
  2. Sets the same `path` on both cookies, then sets different `domain` values (e.g., `c1.setDomain("example.com")` vs `c2.setDomain("other.com")`), and asserts they are **not** equal
  3. Sets the same `domain` and `path` on both cookies, and asserts they **are** equal
  4. Tests that when one cookie has a `null` path and the other has a non-null path (or vice versa), they are correctly recognized as **not** equal
  5. Tests that when one cookie has a `null` domain and the other has a non-null domain (or vice versa), they are correctly recognized as **not** equal
  6. Verifies that two cookies with all `null` paths and `null` domains are considered equal if names match
- The TG should verify that the comparison correctly uses `Objects.equals()` (or equivalent null-safe equality) for each property (name, path, domain) so that `NullPointerException` is not thrown when any property is `null`
- Common pitfalls to avoid:
  - Testing only with non-null path and domain values, missing the `null` property edge cases that can cause `NullPointerException`
  - Testing only the `name` property and assuming path/domain comparisons are correct without explicit verification
  - Using `c1.getPath().equals(c2.getPath())` style comparison that throws `NullPointerException` when `getPath()` returns `null`
  - Not resetting properties between test steps (e.g., after setting `c2.setPath("Path")`, forgetting to set `c1.setPath("Path")` back before testing domain differences)

### Correct test example:
```java
@Test
public void testCookieEqualityWithAllProperties() {
    Cookie c1 = new Cookie("Name", "Value");
    Cookie c2 = new Cookie("Name", "Value");

    // Same name, no path/domain -> equal
    assertTrue(Cookies.isEqual(c1, c2));

    // Different path -> not equal
    c2.setPath("Path");
    assertFalse(Cookies.isEqual(c1, c2));

    // Same path -> equal again
    c1.setPath("Path");
    assertTrue(Cookies.isEqual(c1, c2));

    // Different domain -> not equal
    c2.setDomain("Domain");
    assertFalse(Cookies.isEqual(c1, c2));

    // Same domain -> equal again
    c1.setDomain("Domain");
    assertTrue(Cookies.isEqual(c1, c2));

    // Null path vs non-null path -> not equal
    Cookie c3 = new Cookie("Name", "Value");
    c3.setPath("/somepath");
    assertFalse(Cookies.isEqual(c1, c3));
}
```

### Incorrect test example (pitfalls):
```java
@Test
public void testCookieEqualityIncomplete() {
    Cookie c1 = new Cookie("Name", "Value");
    Cookie c2 = new Cookie("Name", "Value");
    
    // Only tests name equality, never varies path/domain
    assertTrue(Cookies.isEqual(c1, c2));
    
    // Sets path on c2 but not c1, expects false - OK
    c2.setPath("Path");
    assertFalse(Cookies.isEqual(c1, c2));
    
    // BUT: never tests domain difference independently
    // AND: never tests null path vs non-null path
    // AND: never resets path on c1 before testing domain
}
```