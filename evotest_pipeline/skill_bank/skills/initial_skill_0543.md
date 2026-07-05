---
name: ldap-attribute-null-safe-access
description: When reading optional LDAP attributes that may be null from a directory
  entry, tests must cover the scenario where the attribute is missing entirely. This
  skill teaches how to write tests that verify null-safe handling or graceful failure
  for missing/non-existent LDAP attributes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- LDAP_ATTRIBUTE_MISSING_HANDLING
test_pattern: EXCEPTION_TEST
---

# ldap-attribute-null-safe-access

## Instructions

# LDAP Attribute Null-Safe Access

## Instructions

- WHEN the TG encounters code that reads an LDAP attribute via methods like `Entry.getAttribute()` or `Attributes.get()` and then accesses the result's value(s) without a null check (e.g., calling `.get()`, `.iterator()`, `.getValue()`, `.getStringValue()`, or iterating over the result directly)
- THEN the TG should write a test where that specific LDAP attribute is **missing** from the entry (i.e., the attribute is not present in the `Entry`'s attributes), and verify that the code handles it gracefully rather than throwing a `NullPointerException`
- Include concrete values: use a valid LDAP `Entry` object with all required attributes populated, but explicitly omit the attribute under test (e.g., omit the `"uid"` attribute when testing UID-based user lookup)
- Verify that calling the method on the buggy version either:
  - Returns a gracefully handled result (e.g., returns `null`, returns an empty collection, or skips the entry), OR
  - Throws a meaningful exception (e.g., `IllegalArgumentException`, `LdapException`) — but **not** a `NullPointerException`
- Common pitfalls to avoid:
  - **Testing only valid attribute scenarios**: The TG might only test with entries where all attributes are present, missing the null-safety bug
  - **Assuming attribute always exists**: LDAP attributes defined as `optional` or `may` in the schema may not be present on every entry
  - **Testing the wrong exception type**: Expecting `NullPointerException` instead of verifying it does NOT occur, or expecting a specific checked exception when the code swallows the null

### Correct Example (detects the bug)
```java
// Test that listUsers gracefully handles entries missing the 'uid' attribute
@Test
public void testListUsersWithMissingUid() throws Exception {
    // Setup: create LDAP entries where some entries have all attributes
    // but the entry being tested is missing the "uid" attribute
    
    // The method under test should NOT throw NullPointerException
    // when iterating over entries that lack the uid attribute
    
    Iterator<ExternalUser> users = provider.listUsers("someFilter");
    // Verify the iteration proceeds without NPE
    // The missing-uid entry should be skipped or handled gracefully
}
```

### Incorrect Example (does NOT detect the bug)
```java
// Only tests the happy path where all attributes are present
@Test
public void testListUsersWithUid() throws Exception {
    Iterator<ExternalUser> users = provider.listUsers("someFilter");
    // This only works when uid attribute is present
    assertTrue(users.hasNext());
    assertEquals("testUser", users.next().getId());
}
```