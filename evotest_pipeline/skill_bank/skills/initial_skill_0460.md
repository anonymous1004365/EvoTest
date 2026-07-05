---
name: mounted-mapper-compatibility-score-ordering
description: When a CompoundRequestMapper selects among IRequestMapper candidates
  using a compatibility score tie-breaking mechanism, the TG should verify that exact-match
  mappers (with higher compatibility scores) are correctly preferred over parameterized
  optional mappers. Without ordering guarantees, the mapper iteration order may cause
  the wrong mapper to be selected when scores are equal.
code_tags:
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# mounted-mapper-compatibility-score-ordering

## Instructions

# MountedMapper Compatibility Score Ordering

## Instructions

- **WHEN** the TG encounters a `CompoundRequestMapper` that iterates over `IRequestMapper` entries with `MapperWithScore` wrappers and selects one based on a `compatibilityScore` field  
- **THEN** the TG should write a test that:
  1. Mounts two mappers (e.g., via `mount(...)`) — one with an exact path like `/exactMatch` and another with a parameterized optional path like `/prefix/${optionalParam}/something` that overlaps with the exact path
  2. Sends a request that matches the exact path and verifies that the exact match mapper (the one with the higher `getCompatibilityScore()`) is selected
  3. Asserts that the compatibility score of the exact match is **strictly greater** than the compatibility score of the parameterized/optional match
  4. Iterates the mappers in **multiple different orders** (mount the exact mapper first, then swap to mount the parameterized mapper first) to ensure the selection is based on score comparison, not insertion order

- **Concrete example from the bug:** `MountedMapper` mounts an exact path like `"/exactMatch"` and a parameter path like `"/prefix/${optionalParam}"`. The exact mapper should return `getCompatibilityScore() = 2` while the parameterized one returns `2`, but the exact one must actually be **greater**. If both scores are equal (`2 == 2`), the selection defaults to insertion order (first registered wins), which is wrong. The test must verify that swapping the mount order does NOT change the outcome — the exact match always wins.

- **Common pitfalls:**
  - ❌ Testing only one mount order (e.g., always mounting the exact mapper first), which masks the ordering bug
  - ❌ Assuming that equal compatibility scores are fine — the test must assert strict inequality (`scoreExact > scoreParameterized`)
  - ❌ Using `assertEquals()` on the selected mapper without also checking that the compatibility score comparison logic is correct
  - ❌ Only checking that the request *resolves*, not that it resolves to the **correct mapper** (exact match must be preferred)
  - ❌ Not considering that optional/required parameter mappers may produce different compatibility scores that need comparison

- **Correct approach:**
```java
// Mount in one order
tester.getApplication().mount(new MountedMapper("/exactMatch", PageA.class));
tester.getApplication().mount(new MountedMapper("/prefix/${optionalParam}/something", PageB.class));

// Send request for exact match
HttpTester.Request request = HttpTester.newRequest("GET", "/exactMatch");
HttpTester.Response response = HttpTester.parseResponse(tester.processRequest(request, ...));
// Verify the exact match PageA was rendered

// Now unmount and re-mount in opposite order
// Verify the exact match PageA is STILL rendered regardless of mount order
```

- **What to expect on the buggy version:** When both mappers report `getCompatibilityScore() = 2` (or equal scores), the buggy code will pick whichever mapper was registered first, causing the parameterized optional mapper to be selected instead of the exact match one when the mount order is reversed.