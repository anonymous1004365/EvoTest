---
name: account-disabled-state-validation
description: When transferring money between accounts, the TG must verify that both
  debited and credited accounts are checked for enabled/disabled state. Test with
  a disabled recipient account to ensure the system prevents transfers TO disabled
  accounts, not just FROM disabled accounts.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# account-disabled-state-validation

## Instructions

# Account Disabled State Validation

## Instructions

- WHEN the TG encounters a money transfer service that validates the `debitedAccount` (source account) for a disabled/enabled state
- THEN it should ALSO verify that the `creditedAccount` (target/destination account) is independently checked for the disabled/enabled state, and that a transfer TO a disabled target account is rejected with the same or equivalent exception/error
- Specifically, in a `TransferService` with a method like `executeTransfer(request)`, where the buggy version only checks `debitedAccount.isDisabled()` but NOT `creditedAccount.isDisabled()`, the TG should:
  - Create a test case where the `creditedAccount` (target account) has its enabled/disabled flag set to disabled
  - Verify that the transfer is rejected (e.g., by catching an exception, or asserting the transfer was NOT executed)
  - The test should pass on the fixed version (which checks both accounts) and fail on the buggy version (which only checks the debited account)
- Common Pitfalls:
  - Testing only the `debitedAccount` (source) being disabled — this does NOT expose the bug
  - Testing with both accounts enabled — this also does NOT expose the bug
  - Forgetting to handle the exception thrown by the validation logic (e.g., wrapping in try-catch or using `assertThrows`)
  - Testing only for null accounts, missing the disabled-state validation gap

**Correct Example (exposes the bug):**
```java
@Test
public void shouldNotExecuteTransfer_whenTargetAccountIsDisabled() {
    Account source = createEnabledAccount();
    Account target = createDisabledAccount();
    TransferRequest request = new TransferRequest(source.getId(), target.getId(), BigDecimal.TEN);
    
    assertThrows(TransferDisabledAccountException.class, () -> {
        transferService.executeTransfer(request);
    });
}
```

**Incorrect Example (does NOT expose the bug):**
```java
@Test
public void shouldNotExecuteTransfer_whenSourceAccountIsDisabled() {
    Account source = createDisabledAccount();
    Account target = createEnabledAccount();
    TransferRequest request = new TransferRequest(source.getId(), target.getId(), BigDecimal.TEN);
    
    assertThrows(TransferDisabledAccountException.class, () -> {
        transferService.executeTransfer(request);
    });
    // This test passes even on the buggy version, because the buggy version
    // already checks the source account. It does NOT verify the target account check.
}
```