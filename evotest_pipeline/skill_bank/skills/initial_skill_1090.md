---
name: header-name-trimming-and-case-insensitivity
description: WHEN testing HttpHeaderCollection-style APIs that trim whitespace from
  header names, normalize to lowercase, and use case-insensitive lookup — THEN tests
  must cover operations (add, remove, contains, get, getHeaderNames) with whitespace-padded
  names and verify that trimmed, lowercased lookup works correctly across all public
  methods.
code_tags:
- HEADER_NAME_TRIMMING
- VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# header-name-trimming-and-case-insensitivity

## Instructions

# Header Name Trimming and Case-Insensitive Lookup

## Instructions

### WHEN the TG encounters a class like `HttpHeaderCollection` that:
- **Trims leading/trailing whitespace** from header names (e.g., `"name".trim()` in a `HeaderKey` constructor or any normalization step)
- **Uses a case-insensitive key** for internal storage/matching (e.g., converting to lowercase with `toLowerCase(Locale.US)`)
- **Has a chain of public methods** that all call the internal normalization (add, remove, contains, get, getHeaderNames, etc.)

### THEN the TG should:

1. **Test with whitespace-padded names on ALL operations in sequence:**
   - Call `addHeader("   X-Image    ", "value")` — the name gets trimmed in `HeaderKey` constructor, stored as key="x-image"
   - Call `addHeader("X-Image    ", "value2")` — same trimmed key, so both values accumulate under ONE header
   - Call `getHeaderValues("X-IMAGE")` — a new `HeaderKey("X-IMAGE")` gets created, trimmed to "x-image", matches the stored key → returns both values
   - Call `getCount()` — must be 1 (not 2), because both adds mapped to the same normalized key
   - Call `removeHeader(" x-tesT ")` — the trimmed name "x-test" must match the stored key "x-test"

2. **Test explicitly that the `getHeaderNames()` method returns the ORIGINAL name** (the trimmed-but-not-lowercased version stored in `HeaderKey.name`), i.e., if you add with `"   X-Image    "`, `getHeaderNames()` should contain `"X-Image"` (after trim, preserving original case for the first letter).

3. **Test that empty header values (RFC2616) are preserved after trimming:**
   - `setHeader("foobaz", "")` → `getHeader("foobaz")` must be `""` (not null)
   - `setHeader("foobaz", "     ")` → the value is trimmed to `""` → `getHeader("foobaz")` must be `""`

4. **Test removeHeader with whitespace-padded name:**
   - Add header `"X-Test"` with value "foo"
   - Call `removeHeader(" x-tesT ")` — this should remove the header because "x-test" (trimmed) matches the stored key
   - `containsHeader("X-Test")` should return false
   - `isEmpty()` should return true

### Common pitfalls to avoid:

- ❌ Testing only with clean names (no whitespace padding) — this misses the bug where a trimmed name and a non-trimmed lookup fail to match
- ❌ Testing only `addHeader`/`getHeader` in isolation without verifying the full lifecycle: add → add (same name, padded differently) → getValues → getCount → remove → isEmpty
- ❌ Assuming `getHeaderNames()` returns the exact string you passed in — it returns the trimmed version (internal `HeaderKey.name`), not the original padded string
- ❌ Forgetting that both the NAME (in `HeaderKey` constructor) AND the VALUE (in `addHeader`) are trimmed — test value trimming too
- ❌ Testing only with one type of operation (e.g., only add/get) and not the full set (remove, contains, getCount, getHeaderNames, isEmpty, clear)

### Example of a correct test:

```java
HttpHeaderCollection headers = new HttpHeaderCollection();

// Add with whitespace-padded name
headers.addHeader("   X-Image    ", "    jpeg     ");
headers.addHeader("X-Image    ", "    gif     ");

// Values are trimmed; both map to the same key
assertArrayEquals(new String[] { "jpeg", "gif" }, headers.getHeaderValues("X-IMAGE"));

// Only 1 unique header name despite 2 adds
assertEquals(1, headers.getCount());

// Remove with whitespace-padded name works
headers.removeHeader(" x-tesT ");
assertEquals(1, headers.getCount());

// Empty values preserved
headers.setHeader("foobaz", "");
assertEquals("", headers.getHeader("foobaz"));

headers.setHeader("foobaz", "     ");
assertEquals("", headers.getHeader("foobaz"));
```

### Example of an incorrect test (would miss the bug):

```java
HttpHeaderCollection headers = new HttpHeaderCollection();

// ❌ Only tests clean names without whitespace padding
headers.addHeader("X-Image", "jpeg");
headers.addHeader("X-Image", "gif");
assertArrayEquals(new String[] { "jpeg", "gif" }, headers.getHeaderValues("X-Image"));

// ❌ Missing: tests with padded names, getCount after padded adds, 
//   removeHeader with padding, empty value preservation
```