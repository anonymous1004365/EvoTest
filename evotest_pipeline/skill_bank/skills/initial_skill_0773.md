---
name: privilege-upgrade-aggregate-membership-validation
description: When upgrading repository privileges, validate that aggregate privileges
  (like jcr:all) include all expected member privileges. Without proper validation,
  custom or test privileges can be incorrectly included in aggregate privilege definitions
  during upgrade.
code_tags:
- VALIDATION
- STATE_MUTATION
- ACCESS_CONTROL_EVALUATION
test_pattern: STATE_TEST
---

# privilege-upgrade-aggregate-membership-validation

## Instructions

# Privilege Upgrade Aggregate Membership Validation

## Instructions

- WHEN the TG encounters privilege upgrade logic that constructs aggregate privileges (e.g., `jcr:all`) by collecting member privilege names during repository upgrade
- THEN the TG should write a test that:
  1. Creates a repository with known aggregate privilege definitions (e.g., `jcr:all` composed of specific named privileges like `rep:readNodes`, `rep:readProperties`, `jcr:read`, `jcr:write`, `rep:write`, `rep:alterProperties`, etc.)
  2. Upgrades the repository using the upgrade mechanism
  3. After upgrade, verifies that each aggregate privilege contains exactly the expected set of member privileges — no more, no less
  4. Compares the actual members against a known expected set using set equality (order-independent comparison)
  5. Uses `Set` comparison (e.g., `assertEquals(expectedSet, actualSet)`) rather than list comparison to avoid order sensitivity issues
- WHEN constructing the test, include both standard built-in privileges AND any custom/test privileges in the source repository to ensure they are not accidentally merged into standard aggregates
- WHEN verifying aggregate privileges, iterate over all declared aggregate privileges (e.g., using `AccessControlUtils.aggregatePrivileges()`) and check each one's declared aggregate member names
- Common pitfalls to avoid:
  - Testing only that upgrade succeeds without checking the resulting privilege structure
  - Assuming aggregate privileges are unchanged after upgrade without explicit verification
  - Using list comparison when order is non-deterministic (use set comparison instead)
  - Testing only standard privileges without including custom/test privileges that could interfere

### Correct Example (Java/JUnit):
```java
// Verify that after upgrade, jcr:all aggregate privilege contains exactly
// the expected member privileges
Set<String> expected = new HashSet<>(Arrays.asList(
    "rep:readNodes", "rep:readProperties", "rep:addProperties",
    "rep:alterProperties", "rep:removeProperties", "jcr:addChildNodes",
    "jcr:removeChildNodes", "jcr:removeNode", "jcr:readAccessControl",
    "jcr:modifyAccessControl", "jcr:nodeTypeManagement",
    "jcr:versionManagement", "jcr:lockManagement",
    "jcr:lifecycleManagement", "jcr:retentionManagement",
    "jcr:workspaceManagement", "jcr:nodeTypeDefinitionManagement",
    "jcr:namespaceManagement", "rep:privilegeManagement",
    "rep:userManagement", "rep:indexDefinitionManagement",
    "jcr:read", "jcr:modifyProperties", "jcr:write", "rep:write"
));
PrivilegeManager pm = session.getAccessControlManager().getPrivilegeManager();
Privilege jcrAll = pm.getPrivilege("jcr:all");
Set<String> actual = new HashSet<>(Arrays.asList(jcrAll.getDeclaredAggregatePrivilegeNames()));
assertEquals("jcr:all aggregate members mismatch after upgrade", expected, actual);
```

### Incorrect Example (fails to catch the bug):
```java
// BAD: Only checks that upgrade doesn't throw an exception
// Does NOT verify the actual privilege structure
RepositoryUpgrade upgrade = new RepositoryUpgrade(source, target);
upgrade.upgrade();
// No assertion on privilege content — misses the bug entirely!
```

### Incorrect Example (order-sensitive comparison):
```java
// BAD: Using list comparison — order may vary between runs
List<String> expected = Arrays.asList("jcr:read", "rep:write", ...);
List<String> actual = Arrays.asList(jcrAll.getDeclaredAggregatePrivilegeNames());
assertEquals(expected, actual); // May fail on ordering, not content
```