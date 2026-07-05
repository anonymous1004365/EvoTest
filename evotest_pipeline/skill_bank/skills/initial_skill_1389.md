---
name: duplicate-cookie-dedup
description: When a mock servlet response uses custom equality logic (Cookies.isEqual
  via Cookies.Key with name/path/domain) to deduplicate cookies in addCookie(), the
  test must add cookies with different names, paths, and domains to verify the deduplication
  logic correctly handles all equality dimensions and maintains the expected cookie
  count.
code_tags:
- COLLECTION_STATE_MUTATION
- EQUALS_OVERRIDE_RECIPE
test_pattern: STATE_TEST
---

# duplicate-cookie-dedup

## Instructions

# Duplicate Cookie Deduplication in MockHttpServletResponse

## Instructions

- WHEN the TG encounters `MockHttpServletResponse.addCookie(Cookie)` that uses `Cookies.isEqual(cookie, old)` with `Cookies.Key` (which compares `name`, `path`, and `domain` fields) to remove duplicate cookies before adding a new one
- THEN the TG should write a state verification test that:
  1. Adds a cookie with specific `name`, `path`, and `domain` values
  2. Verifies the cookie was added (expect count = 1)
  3. Adds a second, identical cookie (same `name`, `path`, `domain`)
  4. **Asserts that the cookie count remains 1** (the duplicate was removed before adding)
  5. Adds a third cookie with the same `name` but a **different `path`** (e.g., `/other` instead of `null`/default)
  6. **Asserts that the cookie count increases to 2** (different path means different cookie per RFC 2109 §4.3.3)
  7. Adds a fourth cookie with same `name` and `path` as the third but a **different `domain`** (e.g., `example.com` instead of `null`/default)
  8. **Asserts that the cookie count increases to 3** (different domain means different cookie)
  9. Adds a fifth cookie identical to the fourth
  10. **Asserts that the cookie count remains 3** (duplicate removed)
- The test must call `response.getCookies()` to get the current count after each mutation — note that `getCookies()` returns **copies**, so the state test should verify the count via `size()` on the returned `List<Cookie>`, not by checking identity
- **Common pitfalls:**
  - ❌ Testing only by adding two cookies with the same name (default null path/domain) and expecting 1 — this misses testing the path and domain dimensions of the equality logic
  - ❌ Using `Cookie` objects without explicitly calling `setPath()` or `setDomain()` — both default to `null`, so you need to explicitly set different values to reach different branches of the `Cookies.Key.equals()` logic
  - ❌ Forgetting that `getCookies()` returns defensive copies — the test should verify that the internal `cookies` list is being mutated correctly (via `getCookies().size()`) rather than checking reference equality

### Correct Example (from MockHttpServletResponseTest.addDuplicateCookie)
```java
Cookie cookie1 = new Cookie("name", "value");
response.addCookie(cookie1);
assertEquals(1, response.getCookies().size());  // First cookie added

Cookie cookie2 = new Cookie("name", "value");
response.addCookie(cookie2);
assertEquals(1, response.getCookies().size());  // Duplicate removed, still 1

Cookie cookie3 = new Cookie("name", "value");
cookie3.setPath("/");
response.addCookie(cookie3);
assertEquals(2, response.getCookies().size());  // Different path, new cookie

Cookie cookie4 = new Cookie("name", "value");
cookie4.setPath("/");
response.addCookie(cookie4);
assertEquals(2, response.getCookies().size());  // Duplicate of cookie3, still 2

Cookie cookie5 = new Cookie("name", "value");
cookie5.setPath("/");
cookie5.setDomain("example.com");
response.addCookie(cookie5);
assertEquals(3, response.getCookies().size());  // Different domain, new cookie

Cookie cookie6 = new Cookie("name", "value");
cookie6.setPath("/");
cookie6.setDomain("example.com");
response.addCookie(cookie6);
assertEquals(3, response.getCookies().size());  // Duplicate of cookie5, still 3
```

### Incorrect Example
```java
// ❌ Only tests name-based dedup, misses path/domain dimensions
Cookie c1 = new Cookie("name", "value");
response.addCookie(c1);
assertEquals(1, response.getCookies().size());

Cookie c2 = new Cookie("name", "value");
response.addCookie(c2);
assertEquals(1, response.getCookies().size());
// Never verifies that path="/" or domain="example.com" creates unique cookies
```