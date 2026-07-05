---
name: sync-create-user-id-case-sensitivity
description: Teaches the test generator to verify that user creation via external
  identity synchronization correctly handles user IDs that differ only in case (e.g.,
  "testUser" vs "testuser"), ensuring proper comparison and deduplication logic.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# sync-create-user-id-case-sensitivity

## Instructions

# Sync Create User ID Case Sensitivity

## Instructions

- WHEN the TG encounters code that creates or synchronizes external identity users (e.g., `ExternalLoginModule`, `DefaultSyncHandler`, `DynamicSyncContext`) where a user ID from an external identity provider is used to look up or create a local principal/user
- THEN the TG should test that creating a user whose ID differs only in case from an existing user (e.g., first create a user with ID `"testUser"`, then attempt to create a user with ID `"testuser"`) validates the case-insensitive uniqueness logic
  - Specifically, the test should:
    1. Configure the sync handler with ID mapping enabled (or relevant flags)
    2. Call `loginModule.login(...)` and `loginModule.commit()` for a user with a mixed-case ID (e.g., `"testUser"`)
    3. Then call `loginModule.logout()`, set up a new login with a differently-cased ID (e.g., `"testuser"`)
    4. Call `loginModule.login(...)` and `loginModule.commit()` for the second user
    5. Verify that the second call either:
       - Succeeds and returns the same user (if the system treats them as the same identity), OR
       - Throws an appropriate exception (if case-sensitive duplicate IDs are detected)
    6. Verify the resulting state — e.g., the number of principals, user properties, or groups created is correct (not creating duplicate users)
  - Use `@Test` annotated methods and assert on `loginModule.commit()` return value (e.g., `assertTrue`, `assertFalse`) or expected exceptions
  - Include a case where the two IDs are identical in content after case normalization (e.g., `"testUser"` vs `"testuser"`)

- Common pitfalls to avoid:
  - Testing only with distinct user IDs that differ in more than case — this misses the case-sensitivity bug
  - Testing only the login phase without verifying the commit/sync phase where user creation happens
  - Assuming user IDs are always case-sensitive — this skill specifically targets case-insensitive comparison bugs
  - Forgetting to call `loginModule.logout()` between the two login sessions, which may be necessary to clear state
  - Not checking the final state of the system (e.g., principal count, user properties) to verify no duplicate users were created

### Correct example:
```java
@Test
public void testSyncCreateUserCaseInsensitive() throws Exception {
    // Setup first user "testUser"
    loginModule.login();
    loginModule.commit();
    loginModule.logout();
    
    // Setup second user "testuser" (same letters, different case)
    loginModule.login();
    loginModule.commit();
    
    // Verify only one user was created
    // (e.g., check user manager, principal count, etc.)
}
```

### Incorrect example (missing case-insensitivity test):
```java
@Test
public void testSyncCreateUser() throws Exception {
    // Only tests with a unique user ID "testUser"
    loginModule.login();
    loginModule.commit();
    // Does NOT test with "testuser" — misses the bug
}
```