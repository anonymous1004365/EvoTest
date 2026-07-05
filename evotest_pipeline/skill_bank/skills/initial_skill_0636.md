---
name: foreign-group-membership-state-corruption
description: When synchronizing external identity memberships, the TG must test that
  foreign groups (groups not owned by the current IDP) do not get incorrectly modified
  or have their membership state corrupted during sync operations.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# foreign-group-membership-state-corruption

## Instructions

# Foreign Group Membership State Integrity

## Instructions

**WHEN** the TG encounters code that synchronizes external identity memberships (e.g., `DefaultSyncContext` sync methods that process group memberships and create/update authorizable identities):

- **THEN** the TG MUST write a test that verifies foreign groups (groups belonging to a different IdentityProvider) are NOT modified or disrupted during the sync of a user from a different IDP.

- Specifically, the test MUST:
  1. Create a foreign group authorizable (e.g., using `TestPrincipalProvider.FOREIGN_GROUP_PRINCIPAL_NAME` = `"foreignGroup"`) that belongs to a different IDP (set its intermediate path to a different provider's prefix via `user.getPrincipalName()` and `syncConfig` such that the sync result is `SyncResult.Status.FOREIGN`).
  2. Add the foreign group as a member of an existing authorizable (e.g., an external user being synced).
  3. Perform the sync operation (e.g., `syncMembership` or `sync` on the sync context).
  4. **Assert** that the foreign group's membership list does NOT contain the synced user — the group's `getDeclaredMembers()` should not include the external user's principal after sync.
  5. **Assert** that no exception is thrown during the sync process.

- **Common pitfalls**:
  - Testing only with groups managed by the same IDP (internal groups) and not testing with foreign groups.
  - Failing to verify that the foreign group's member set remains unmodified after sync.
  - Assuming the sync operation will throw an exception for foreign groups — the bug is silent data corruption (the foreign group gains or loses members incorrectly).
  - Not setting up the sync configuration (`SyncConfig`) properly so the group is recognized as foreign (e.g., not setting `syncConfig.getUser().setMembershipNestingDepth(-1)` or equivalent).

- **Concrete example** (correct test pattern):
  ```java
  // Arrange
  ExternalUser externalUser = createTestExternalUser();
  Group foreignGroup = createForeignGroup(); // belongs to different IDP
  foreignGroup.addMember(externalUser.getPrincipal()); // foreignGroup lists externalUser as member
  syncConfig.getUser().setMembershipNestingDepth(-1); // enable full membership sync
  
  // Act
  DefaultSyncContext syncCtx = new DefaultSyncContext(syncConfig, userManager, provider);
  syncCtx.sync(externalUser, DEFAULT_SYNC_RESULT); // sync the external user
  
  // Assert — foreign group should NOT include externalUser after sync
  assertFalse("Foreign group should not be modified by sync", 
      foreignGroup.getDeclaredMembers().contains(externalUser.getPrincipal()));
  ```

- **Incorrect test pattern** (what NOT to do):
  ```java
  // Only testing internal group membership — misses the bug
  Group internalGroup = createInternalGroup();
  internalGroup.addMember(externalUser.getPrincipal());
  syncCtx.sync(externalUser, ...);
  assertTrue(internalGroup.getDeclaredMembers().contains(externalUser.getPrincipal()));
  // This test passes on the buggy code, missing the silent foreign group corruption.
  ```