---
name: equals-hashcode-null-field-consistency
description: When overriding equals() and hashCode() in classes with nullable fields,
  ensure both methods treat null fields consistently to avoid breaking the equals/hashCode
  contract. This skill helps detect bugs where equals() returns true for two objects
  but hashCode() returns different values due to conditional null handling.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# equals-hashcode-null-field-consistency

## Instructions

# Equals/HashCode Consistency with Nullable Fields

## Instructions

- WHEN the TG encounters a class that overrides both `equals()` and `hashCode()`, and has fields that can be `null` (e.g., `String scheme`, `byte[] auth` in `ZooKeeperConnectionInfo`)
- THEN the TG should test that the `equals()` / `hashCode()` contract is respected for all combinations of null and non-null values of nullable fields
- Specifically:
  - WHEN creating two objects with the same non-null values for required fields (e.g., `keepers = "localhost:2181"`, `timeout = 60000`) AND the same **null** values for optional fields (e.g., `scheme = null`, `auth = null`)
  - THEN `assertEquals(obj1, obj2)` must pass AND `assertEquals(obj1.hashCode(), obj2.hashCode())` must also pass

- Common pitfalls to avoid:
  - **Testing only non-null combinations**: When all fields are non-null and equal, hashCode() may coincidentally match even if the contract is broken for null fields. Always test with null fields too.
  - **Testing only equals without hashCode**: A test that only checks `assertEquals(a, b)` can pass even if `hashCode()` is broken, because `Assert.assertEquals()` uses `equals()` directly. The hashCode violation will cause failures in hash-based collections (HashMap, HashSet, etc.) at runtime.
  - **Assuming HashCodeBuilder is correct automatically**: Apache Commons Lang `HashCodeBuilder.append(field)` may or may not handle null correctly depending on version. When `hashCode()` only conditionally appends non-null fields (using `if (null != field) { hcb.append(field); }`), but `equals()` correctly handles null comparisons, the contract is violated.
  - **Testing only with non-null `scheme` and `auth`**: The bug in `ZooKeeperConnectionInfo.hashCode()` only manifests when ALL nullable fields are null, because the `HashCodeBuilder` is initialized with `hashCode = 31`, then `append(keepers)` and `append(timeout)` are called. The conditionals `if (null != scheme)` and `if (null != auth)` skip those appends, so objects with null scheme AND null auth both have `hashCode = 31 * keepers.hashCode() + timeout`. The bug occurs only in this specific null combination.

### Correct test example:
```java
@Test
public void testEqualityWithNullFields() {
    // Both objects have all nullable fields set to null
    ZooKeeperConnectionInfo obj1 = new ZooKeeperConnectionInfo("localhost:2181", 60000, null, null);
    ZooKeeperConnectionInfo obj2 = new ZooKeeperConnectionInfo("localhost:2181", 60000, null, null);
    
    // Both assertions MUST pass for contract compliance
    Assert.assertEquals(obj1, obj2);
    Assert.assertEquals(obj1.hashCode(), obj2.hashCode());
}
```

### Incorrect test (missing hashCode check, insufficient coverage):
```java
@Test
public void testEquality() {
    // Only checks equals(), not hashCode()
    Assert.assertEquals(
        new ZooKeeperConnectionInfo("localhost:2181", 60000, null, null),
        new ZooKeeperConnectionInfo("localhost:2181", 60000, null, null));
    // Missing: Assert.assertEquals(hc1, hc2);
}
```

### Another incorrect approach (testing only non-null fields):
```java
@Test
public void testEqualityWithNonNullFields() {
    // Both have non-null scheme and auth - this would pass even with the bug
    ZooKeeperConnectionInfo obj1 = new ZooKeeperConnectionInfo("localhost:2181", 60000, "digest", new byte[]{1,2,3});
    ZooKeeperConnectionInfo obj2 = new ZooKeeperConnectionInfo("localhost:2181", 60000, "digest", new byte[]{1,2,3});
    Assert.assertEquals(obj1, obj2);
    Assert.assertEquals(obj1.hashCode(), obj2.hashCode()); // This would pass even with the bug
}
```