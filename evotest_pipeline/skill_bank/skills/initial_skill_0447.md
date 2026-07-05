---
name: auditing-handler-null-entity-skip
description: When testing auditing handlers that process entities with optional identifiers,
  the TG should verify that entities lacking an identifier are properly skipped rather
  than causing errors or being processed. This skill applies to IsNewAwareAuditingHandler
  and similar auditing interceptors.
code_tags:
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# auditing-handler-null-entity-skip

## Instructions

# Auditing Handler Null Entity Identifier Skipping

## Instructions

- WHEN the TG encounters an `IsNewAwareAuditingHandler` (or similarly named auditing handler) with a method like `markAudited`, `handle`, `onApplicationEvent`, or `afterLoad` that accepts entity objects with potentially null identifiers
- THEN the TG should write a test that provides an entity whose identifier-returning method returns `null`, and verify the handler does NOT throw an exception and does NOT modify the entity (i.e., it silently skips it)
- Specifically, use an entity class that implements `Persistable` or `IsNewAware` where `getId()` (or equivalent) returns `null` and `isNew()` returns `true`
- Verify that after calling the handler method, the entity is not audited — for example, no `setLastModifiedDate(...)` or `setCreatedDate(...)` calls were made, and no `Persistable` audit fields were populated
- Expect that the buggy version might attempt to dereference a null identifier or unconditionally set audit metadata, causing either a `NullPointerException` or incorrect state modification
- The test should confirm the entity's state is unchanged and no exception propagates

### Common Pitfalls
- Do NOT only test entities with non-null identifiers — this misses the null-identifier skip logic entirely
- Do NOT assume the handler throws on null identifiers — the correct behavior is SILENT SKIP
- Do NOT forget to verify both that no exception is thrown AND that the entity state is unchanged (e.g., null audit timestamps remain null)
- Do NOT test only one entity type — if the handler is generic, test with both entity types that supply identifiers and those that don't

### Correct Example (verifying skip behavior)

```java
@Test
void skipsEntityWithoutIdentifier() {
    // Given an entity without an identifier
    var entity = new MyEntity();
    entity.setId(null); // no identifier set
    entity.setCreatedDate(null);

    // When the auditing handler processes it
    assertDoesNotThrow(() -> handler.markAudited(entity));

    // Then the entity should remain un-audited
    assertNull(entity.getCreatedDate(), "Entity without ID should not be audited");
}
```

### Incorrect Example (missing skip test)

```java
@Test
void auditsEntityWithIdentifier() {
    // Only tests the happy path — misses the null-ID skip case
    var entity = new MyEntity();
    entity.setId(42L);
    handler.markAudited(entity);
    assertNotNull(entity.getCreatedDate());
}
```