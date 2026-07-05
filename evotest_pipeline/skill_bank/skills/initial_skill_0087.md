---
name: principal-equality-by-name-validation
description: WHEN testing access control list (ACL) implementations with custom Principal
  objects WHERE equality is based on getName() rather than object identity THEN test
  that addAccessControlEntry and addEntry correctly deduplicate entries with same-named
  but different Principal implementations.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# principal-equality-by-name-validation

## Instructions

# Principal Equality by Name in Access Control Lists

## Instructions

- WHEN the TG encounters an ACL implementation that stores ACE entries in a list (e.g., `List<ACE> entries`)
  - AND the ACE class implements `equals()` based on `principal.getName()` (string comparison) rather than `principal ==` (identity comparison)
  - THEN the TG MUST write tests that verify entries with different Principal objects but the same name are treated as duplicates (not added twice)

- WHEN the TG sees `addAccessControlEntry(Principal, Privilege[])` or `addEntry(Principal, Privilege[], boolean, ...)` being tested:
  - AND two different Principal objects have the same `getName()` return value (e.g., `new PrincipalImpl("anonymous")` vs an anonymous `Principal` with `getName()` returning `"anonymous"`)
  - THEN the TG MUST verify that adding a second entry with the same principal name **does not** create a duplicate entry in the ACL
  - Specifically:
    - First call: `acl.addAccessControlEntry(new PrincipalImpl("anonymous"), privilegesFromNames(JCR_READ))` → returns `true`
    - Second call: `acl.addAccessControlEntry(anotherPrincipalWithSameName("anonymous"), privilegesFromNames(JCR_READ_ACCESS_CONTROL))` → returns `false` (because the entry is already present by name comparison)
    - After both calls, `acl.getAccessControlEntries().length` should be `1`, not `2`

- WHEN the TG writes assertions for ACL entry count:
  - THEN the TG MUST check `acl.getAccessControlEntries().length` (size of the access control entries array)
  - AND NOT just check the return value of `addAccessControlEntry` / `addEntry`

- Common pitfalls to avoid:
  - ❌ Testing only with the same Principal object (identity) — this misses the bug entirely
  - ❌ Assuming different Principal implementations with the same name are different entries
  - ❌ Checking only the boolean return value of `addAccessControlEntry` without verifying the total entry count
  - ❌ Using only `PrincipalImpl` instances (which are checked by `checkValidPrincipal` differently from custom Principals) when the bug specifically manifests with custom Principal implementations
  - ❌ Not testing the dual path: `addAccessControlEntry` (which delegates to `addEntry` with `isAllow=true`) AND `addEntry` separately

## Example

### Correct test (catches the bug):
```java
@Test
public void testAddEntriesWithCustomPrincipal() throws Exception {
    Principal oakPrincipal = new PrincipalImpl("anonymous");
    Principal principal = new Principal() {
        @Override
        public String getName() {
            return "anonymous";
        }
    };

    assertTrue(acl.addAccessControlEntry(oakPrincipal, privilegesFromNames(JCR_READ)));
    // Both principals have getName() == "anonymous", so this should be a duplicate
    assertFalse(acl.addAccessControlEntry(principal, privilegesFromNames(JCR_READ_ACCESS_CONTROL)));
    // Only 1 entry should exist because the second one matched by name
    assertEquals(1, acl.getAccessControlEntries().length);
}
```

### Incorrect test (misses the bug):
```java
@Test
public void testAddEntries() throws Exception {
    Principal principal = new PrincipalImpl("anonymous");

    assertTrue(acl.addAccessControlEntry(principal, privilegesFromNames(JCR_READ)));
    assertTrue(acl.addAccessControlEntry(principal, privilegesFromNames(JCR_READ_ACCESS_CONTROL)));
    // This would return true (both added separately because same object identity check)
    assertEquals(2, acl.getAccessControlEntries().length);
    // Test passes but doesn't catch the real bug with different Principal objects sharing the same name
}
```