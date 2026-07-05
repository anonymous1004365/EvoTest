---
name: group-member-property-migration
description: When migrating user/group membership properties during repository upgrade,
  the TG should test that group member-of relationships survive the upgrade, especially
  when a group's own membership references (rep:members/properties) are being rewritten
  and may be prematurely cleared before verification.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# group-member-property-migration

## Instructions

# Group Member Property Migration

## Instructions

- WHEN the TG encounters repository upgrade code that rewrites `rep:members` properties or migrates group member-of relationships using classes like `GroupEditor`, `GroupEditorProvider`, or `MembershipWriter`:
  - THEN the TG should test that after migration the `Member` interface's `getMemberOf()` method correctly reports the groups that a member belongs to.
  - Specifically, the TG should verify that a user/principal who was added as a member of a group BEFORE the upgrade still shows that group in its `memberOf` list AFTER the upgrade completes (i.e., the `rep:members` property on the group side AND the member-of references on the member side both survive).
  - The test must call `getMemberOf()` on a member node (using the `UserManager.getAuthorizable()` and `Member.getMemberOf()`) and assert that the returned `Iterator<Authorizable>` includes the expected group.
  - The test should catch `RepositoryException` or `RuntimeException` if the member-of information is lost or corrupted (e.g., `Iterator` is empty, or an exception is thrown due to missing/malformed references).
  - Common pitfalls:
    - NOT verifying that the group still has its members listed via `Member.getMemberOf()` after migration.
    - Only testing that the group has members on its own node (e.g., via property read from the group node), but failing to test the reverse reference from the member back to the group.
    - Writing a test that checks only one direction of the membership relationship when the bug lies in the reverse (member-of) direction.
    - Assuming membership is stored as a simple property when it may be stored as a reference list that can be cleared prematurely during migration.
- Example of correct test pattern (Java/JUnit):
  ```java
  @Test
  public void verifyMemberOf() throws Exception {
      Session session = getAdminSession();  // or similar
      UserManager userMgr = getUserManager(session);
      Authorizable testMember = userMgr.getAuthorizable("testuser@example.com");
      assertTrue("Member should have groups", testMember instanceof Member);
      Iterator<Authorizable> memberOf = ((Member) testMember).getMemberOf();
      List<Authorizable> groups = new ArrayList<>();
      memberOf.forEachRemaining(groups::add);
      
      // After migration, the group that testuser was added to must still appear
      boolean found = groups.stream()
          .anyMatch(g -> "testgroup".equals(g.getID()));
      assertTrue("testuser should be member of testgroup after upgrade", found);
  }
  ```
- Example of incorrect test pattern:
  ```java
  @Test
  public void verifyMemberOf() {
      // ❌ Only checks group side, does not check reverse reference
      // ❌ Does not actually verify memberOf relationship
      Group group = userMgr.getAuthorizable("testgroup", Group.class);
      Iterator<Authorizable> members = group.getMembers();
      assertTrue(members.hasNext());
      
      // ❌ Missing: checking that each member still sees the group in getMemberOf()
  }
  ```