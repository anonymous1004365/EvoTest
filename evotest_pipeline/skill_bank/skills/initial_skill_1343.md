---
name: duplicate-access-control-entry-filtering
description: When collecting effective access control entries from a JCR/OAK repository,
  ensure that duplicate entries (same principal, same path, same privileges) are filtered
  out. The test should set up multiple identical ACEs and assert that getEffectivePolicies
  returns unique entries.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# duplicate-access-control-entry-filtering

## Instructions

# Duplicate Access Control Entry Filtering

## Instructions

- WHEN the TG encounters code that collects or returns effective access control entries/policies from `AccessControlManager.getEffectivePolicies()` or similar aggregate methods — particularly in an OAK/JCR repository where multiple identical ACEs could be set programmatically (e.g., due to multiple `setPolicy` calls)
- THEN the TG should write a test that:
  1. Sets up duplicate access control entries for the same principal (e.g., `testUser`) on the same node (e.g., the root node `/`)
  2. Calls `getEffectivePolicies(AccessControlConstants.REP_READ)` or equivalent method to retrieve effective policies
  3. Verifies that the returned list does NOT contain duplicate `AccessControlEntry` objects — i.e., calling `getAccessControlEntries()` on the resulting policies yields exactly 1 entry per expected privilege, not 3
  4. Expects an assertion like `assertEquals(1, aces.size())` or `assertEquals(expectedCount, actualCount)` where duplicates should be removed
- **Common pitfalls**: 
  - Testing only a single privilege type without setting up duplicates
  - Not calling `getEffectivePolicies()` and instead testing `getPolicies()` or `getAccessControlList()` which may not de-duplicate
  - Assuming that `setPolicy` replaces previous identical policies rather than appending them
  - Forgetting to set the repo as "effective" (using `AccessControlConstants.REP_READ`) instead of local path permissions alone

- **Correct example (Java/JUnit)**:
  ```java
  @Test
  public void testNoEffectiveDuplicateEntries() throws Exception {
      // Set up duplicate ACEs for the same principal
      AccessControlManager acMgr = getAccessControlManager();
      Privilege[] readPrivileges = privilegesFromNames(PrivilegeConstants.JCR_READ);
      
      // Add same ACE multiple times
      AccessControlList acl = getAccessControlList(acMgr, null);
      acl.addEntry(testPrincipal, readPrivileges, true);
      acMgr.setPolicy(null, acl);
      acMgr.setPolicy(null, acl);  // duplicate
      
      // Now get effective policies — these should deduplicate
      AccessControlPolicy[] policies = acMgr.getEffectivePolicies(null);
      AccessControlList effAcl = (AccessControlList) policies[0];
      AccessControlEntry[] entries = effAcl.getAccessControlEntries();
      
      // Only 1 unique entry should remain
      assertEquals(1, entries.length);
  }
  ```

- **Incorrect example**:
  ```java
  @Test
  public void testEffectivePolicies() throws Exception {
      // Only sets one policy, never tests duplicates
      AccessControlList acl = getAccessControlList(acMgr, null);
      acl.addEntry(testPrincipal, readPrivileges, true);
      acMgr.setPolicy(null, acl);
      
      // Only checks that it works at all, not that duplicates are filtered
      AccessControlPolicy[] policies = acMgr.getEffectivePolicies(null);
      assertNotNull(policies);
  }
  ```