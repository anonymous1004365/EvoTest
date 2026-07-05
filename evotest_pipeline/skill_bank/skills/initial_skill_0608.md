---
name: provider-name-conversion-to-null
description: When a constructor normalizes null or empty strings to null for a provider
  name field, tests must verify that strings reconstructed from serialized form correctly
  preserve this null normalization. This skill teaches testing round-trip conversion
  through string representation.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# provider-name-conversion-to-null

## Instructions

# Provider Name Null Normalization Testing

## Instructions

- WHEN the Test Generator encounters a constructor that converts both null and empty String providerName values to null (as in `ExternalIdentityRef(@Nonnull String id, @CheckForNull String providerName)` where `this.providerName = (providerName == null || providerName.isEmpty()) ? null : providerName`)
- THEN it MUST create a round-trip serialization test that:
  1. Creates an instance with an empty-string provider name (e.g., `""`)
  2. Gets the string representation via `getString()`
  3. Reconstructs the object via `fromString(getString())`
  4. Asserts that the reconstructed object's `getProviderName()` returns `null`
  5. Asserts that the reconstructed object is `.equals()` to the original

- WHEN testing `getProviderName()` directly
- THEN assert that `getProviderName()` returns `null` for both `new ExternalIdentityRef("id", null)` AND `new ExternalIdentityRef("id", "")`

- Common pitfalls to avoid:
  - Testing only `null` providerName but not `""` (empty string) — the bug is that both normalize to null, and the serialization round-trip must preserve this
  - Testing `getString()` only without the reconstruction — the critical path is `fromString(getString())` which may produce different normalization behavior
  - Forgetting to check `.equals()` between original and reconstructed objects

**Correct example (catches the bug):**
```java
@Test
public void testRoundTripEmptyProviderName() {
    ExternalIdentityRef ref = new ExternalIdentityRef("testId", "");
    ExternalIdentityRef roundTripped = ExternalIdentityRef.fromString(ref.getString());
    
    assertNull("getProviderName() should be null for empty provider", ref.getProviderName());
    assertNull("Round-tripped provider name should also be null", roundTripped.getProviderName());
    assertEquals("Round-tripped ref should equal original", ref, roundTripped);
}
```

**Incorrect example (misses the bug):**
```java
@Test
public void testNullProviderName() {
    ExternalIdentityRef ref = new ExternalIdentityRef("testId", null);
    assertNull(ref.getProviderName());  // only tests null, not empty string round-trip
}
```