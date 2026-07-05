---
name: account-hierarchy-disabled-check
description: When disabling an account, verify that the system checks for enabled
  child accounts before allowing the disable operation. This skill applies to hierarchical
  account management where parent-child relationships must be validated before state
  changes.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# account-hierarchy-disabled-check

## Instructions

# Account Hierarchy Disabled Check

## Instructions

- WHEN the TG encounters a method that disables or deactivates an account (e.g., `disableAccount`, `deactivate`, `setActive(false)`) in a system where accounts have hierarchical parent-child relationships
- THEN it should verify that the method throws an appropriate exception (e.g., `IllegalStateException`, `BusinessException`, `CannotDisableAccountException`) when attempting to disable a parent account that still has enabled child accounts
- The test should: (1) set up a parent account, (2) create one or more child accounts under that parent that are enabled, (3) attempt to disable the parent account, (4) assert that the expected exception is thrown with a message indicating enabled children prevent disabling
- Common pitfalls: (a) testing only with no children — this misses the bug entirely; (b) testing with disabled children only — this also won't trigger the validation; (c) forgetting to persist child accounts before attempting the disable — the check may query the database for children; (d) checking only the exception type without verifying the error message contains relevant context like "children" or "enabled"

- Example correct test:
```java
@Test(expected = IllegalStateException.class)
public void shouldNotDisableAccountWhenHasEnabledChildren() {
    Account parent = new Account();
    parent.setActive(true);
    accountDao.save(parent);
    
    Account child = new Account();
    child.setParentId(parent.getId());
    child.setActive(true);
    accountDao.save(child);
    
    accountManager.disableAccount(parent.getId());
}
```

- Example incorrect test (misses the bug):
```java
@Test
public void shouldDisableAccount() {
    Account account = new Account();
    account.setActive(true);
    accountDao.save(account);
    
    // This passes even on buggy code because there are no children
    accountManager.disableAccount(account.getId());
    assertFalse(account.isActive());
}
```