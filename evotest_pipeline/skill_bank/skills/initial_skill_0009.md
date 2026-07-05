---
name: duplicate-address-detection
description: WHEN testing API helper classes that manage address resources, THEN verify
  that duplicate address detection correctly prevents adding addresses with the same
  name and address space. This skill focuses on validating that address uniqueness
  constraints are enforced across combined name+namespace+address-space tuples.
code_tags:
- VALIDATION
- STATE_MUTATION
- DUPLICATE_ADDRESS_DETECTION
test_pattern: STATE_TEST
---

# duplicate-address-detection

## Instructions

# Duplicate Address Detection in Resource Management

## Instructions

WHEN the TG encounters a class responsible for managing a collection of address resources (e.g., `AddressApiHelper`) that should enforce uniqueness constraints:

- THEN the TG should test that attempting to add a duplicate address (same name, same namespace, same address space) causes an appropriate error/exception to be thrown. The test should verify that the system does NOT silently accept or overwrite the duplicate.

- THEN the TG should test that addresses with the SAME name but DIFFERENT address spaces are treated as DIFFERENT (non-duplicate) resources and both can be added successfully without any exception.

- THEN the TG should test that the state of the address collection before and after adding a duplicate should remain unchanged (i.e., the duplicate add operation should be a no-op or throw an exception, not modify the collection).

- THEN the TG should verify that the error/failure message contains concrete terms related to the duplication, such as "duplicate", "already exists", or the address name itself.

- Common pitfalls: Do NOT assume that same-named addresses are always duplicates — address space is a critical disambiguating dimension. Do NOT forget to verify both the positive case (non-duplicates succeed) and the negative case (duplicates are rejected). Do NOT rely solely on return values — verify the collection state did not change.

### Example of a correct test (pseudocode):
```java
@Test
public void testDuplicateAddressDetection() {
    Address a1 = createAddress("addr1", "space1");
    Address a2 = createAddress("addr1", "space1"); // duplicate
    Address a3 = createAddress("addr1", "space2"); // different space

    helper.addAddress(a1);  // should succeed
    assertThrows(SomeException.class, () -> helper.addAddress(a2));
    
    // same name, different space — should succeed
    helper.addAddress(a3);
    
    // Verify state
    assertEquals(2, helper.getAddresses().size());
}
```

### Example of an incorrect test (missing namespace/address-space consideration):
```java
@Test
public void testDuplicateAddress_INCORRECT() {
    Address a1 = createAddress("addr1");
    Address a2 = createAddress("addr1");
    
    helper.addAddress(a1);
    // WRONG: This might throw on buggy code only for same address space
    assertDoesNotThrow(() -> helper.addAddress(a2));
}
```