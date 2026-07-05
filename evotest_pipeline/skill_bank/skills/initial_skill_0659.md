---
name: privilege-from-name-null-handling
description: Test that privilegeFromName throws RepositoryException when the underlying
  PrivilegeManager returns null for an unknown privilege name, protecting against
  NullPointerException. This applies when testing AccessControlManager implementations
  that delegate to PrivilegeManager.getPrivilege().
code_tags:
- VALIDATION
- NULL_CHECK
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# privilege-from-name-null-handling

## Instructions

# PrivilegeFromName Null Handling

## Instructions

- WHEN the TG encounters an implementation of `AccessControlManager` where the `privilegeFromName(String)` method delegates to a `PrivilegeManager.getPrivilege(String)` method that may return `null` for unknown/non-registered privilege names
- THEN the TG should write a test that calls `privilegeFromName` with an unknown privilege name (e.g., `"unknownPrivilege"`, `""`, or a non-existent JCR privilege name) and verify that a `RepositoryException` is thrown
- The test should mock the underlying `PrivilegeManager.getPrivilege(String)` method to return `null` for the unknown privilege name, and verify that the `privilegeFromName` method propagates a `RepositoryException` rather than throwing a `NullPointerException`
- Include a test that tries an empty string as the privilege name to ensure proper validation exists at this boundary

### Common pitfalls to avoid

- Testing only with registered/valid privilege names like `PrivilegeConstants.JCR_READ` — this only validates the happy path and misses the null-return case entirely
- Assuming `PrivilegeManager.getPrivilege()` always returns a non-null value — in production, unknown privilege names return null
- Writing a test that expects the `NullPointerException` itself (from the null return) rather than checking that the method wraps the null in a `RepositoryException`

### Correct example

```java
@Test(expected = RepositoryException.class)
public void testPrivilegeFromNameWithUnknownPrivilege() throws Exception {
    String unknownPrivilegeName = "unknownPrivilege";
    // assuming privilegeManager.getPrivilege(unknownPrivilegeName) returns null
    acMgr.privilegeFromName(unknownPrivilegeName);
}

@Test(expected = RepositoryException.class)
public void testPrivilegeFromNameWithEmptyPrivilege() throws Exception {
    acMgr.privilegeFromName("");
}
```

### Incorrect example

```java
// WRONG: Only tests with valid privilege names — misses the null-handling bug
@Test
public void testPrivilegeFromName() throws Exception {
    Privilege p = acMgr.privilegeFromName(PrivilegeConstants.JCR_READ);
    assertEquals(PrivilegeConstants.JCR_READ, p.getName());
}

// WRONG: Expects NullPointerException instead of RepositoryException
@Test(expected = NullPointerException.class)
public void testPrivilegeFromNameWithUnknown() throws Exception {
    acMgr.privilegeFromName("unknownPrivilege");
}
```