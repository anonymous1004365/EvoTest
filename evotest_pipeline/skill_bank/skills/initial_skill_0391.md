---
name: admin-user-protection-testing
description: WHEN testing validation of admin user removal or parent folder deletion,
  THEN the TG should test both direct node removal and parent folder removal, verifying
  that CommitFailedException is thrown in both cases. This skill prevents missing
  tests for hierarchical deletion scenarios where protected users can be removed indirectly
  via their parent folder.
code_tags:
- VALIDATION
- CHILD_REMOVAL
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# admin-user-protection-testing

## Instructions

# Admin User Protection Testing

## Instructions

### WHEN the TG encounters code that validates removal of sensitive/protected user nodes (e.g., admin user):
- **THEN** the TG should identify if there is a validator (like `UserValidator`) that intercepts `childNodeDeleted()` calls to check if the deleted node is a protected user via a method like `isAdminUser()`.
- **THEN** the TG should verify that validation checks occur on the *deleted child node*, not on `parentBefore` or `parentAfter`.
- **THEN** the TG should test **two distinct scenarios**:
  1. **Direct deletion of the protected user node**: Remove the user's own Tree node directly (e.g., `root.getTree(admin.getPath()).remove()`).
  2. **Indirect deletion via parent folder removal**: Remove the parent folder node that contains the protected user (e.g., `root.getTree(admin.getPath()).getParent().remove()`), which triggers `childNodeDeleted` on the folder's validator with the user as a child.
- **THEN** the TG should verify that **both** scenarios throw a `CommitFailedException` with the appropriate error message (e.g., `"The admin user cannot be removed"` or similar constraint violation message, typically a 400 ConstraintViolation with code like 27).
- **THEN** the TG should use the actual configured admin ID, retrieved via configuration (e.g., `ConfigurationParameters.getConfigValue(PARAM_ADMIN_ID, DEFAULT_ADMIN_ID)`), and look up the admin authorizable via `UserManager.getAuthorizable(adminId)`.
- **THEN** the TG should ensure the test does a `root.commit()` after looking up or creating the admin and uses `fail("expected message")` + catch `CommitFailedException` pattern.

### Common pitfalls to avoid:
- **Testing only direct node deletion** — The bug was that removing the parent folder of the admin user (e.g., `admin.getPath().getParent()`) bypassed the validation because the `childNodeDeleted()` method used `parentBefore.getChild(name)` to find the correct child tree. If the test only checks direct deletion of the user node, it misses the case where the entire parent folder (which is a `rep:AuthorizableFolder`) is removed.
- **Not checking `childNodeDeleted` logic** — The TG might incorrectly assume the validation happens in `childNodeChanged` or `propertyDeleted`. The relevant validation for removal is in `childNodeDeleted()`.
- **Using literal "admin" string** — The admin ID is configurable via `PARAM_ADMIN_ID`. Always look it up from configuration rather than hardcoding.
- **Forgetting to get authorizable via UserManager** — The test must first get or create the admin authorizable to obtain its path for deletion.

### Example:

**Correct test (catches the bug):**
```java
@Test
public void testRemoveAdminUserFolder() throws Exception {
    try {
        String adminId = getConfig().getConfigValue(PARAM_ADMIN_ID, DEFAULT_ADMIN_ID);
        UserManager userMgr = getUserManager(root);
        Authorizable admin = userMgr.getAuthorizable(adminId);
        if (admin == null) {
            admin = userMgr.createUser(adminId, adminId);
            root.commit();
        }
        // Remove the PARENT folder, which contains the admin user
        root.getTree(admin.getPath()).getParent().remove();
        root.commit();
        fail("Admin user cannot be removed");
    } catch (CommitFailedException e) {
        // success
    } finally {
        root.refresh();
    }
}
```

**Incorrect test (misses the bug):**
```java
@Test
public void testRemoveAdminUser() throws Exception {
    try {
        String adminId = "admin";
        UserManager userMgr = getUserManager(root);
        Authorizable admin = userMgr.getAuthorizable(adminId);
        // Only tests direct node deletion — misses parent folder case
        root.getTree(admin.getPath()).remove();
        root.commit();
        fail("Admin user cannot be removed");
    } catch (CommitFailedException e) {
        // success
    }
}
```