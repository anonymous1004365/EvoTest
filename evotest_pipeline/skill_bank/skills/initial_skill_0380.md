---
name: membership-threshold-split-type-mismatch
description: When upgrading repository groups with member reference splitting at a
  threshold, the test must verify that group nodes are created with the correct primary
  type (rep:Group vs rep:MemberReferencesList) depending on whether the member count
  crosses the DEFAULT_MEMBERSHIP_THRESHOLD (100). This skill helps test the type assignment
  logic during group member split upgrades.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- COLLECTION_OPERATIONS
test_pattern: STATE_TEST
---

# membership-threshold-split-type-mismatch

## Instructions

# Membership Threshold Split Type Mismatch

## Instructions

- WHEN the TG encounters code that performs group member splitting during repository upgrade, where group members are split into `rep:MemberReferences` nodes when the member count exceeds `DEFAULT_MEMBERSHIP_THRESHOLD` (default value 100)
- THEN the TG should write a test that:
  1. Creates a group node (primary type `rep:Group`) with more than 100 members
  2. Performs the upgrade/split operation
  3. Verifies that the resulting group node has the correct primary node type (`rep:Group`), not `rep:MemberReferencesList`
  4. Verifies that member reference child nodes exist with type `rep:MemberReferences`
  5. Expects the test to fail on the buggy version with an error like "Failed to copy content" because group type gets incorrectly changed to `rep:MemberReferencesList`

- Common pitfalls to avoid:
  - Testing only groups with fewer than 100 members (which won't trigger the split logic)
  - Testing the split logic in isolation without verifying the parent group's node type after the split
  - Checking only the existence of member references without verifying the original group's primary type is preserved
  - Using a mock or stub that doesn't exercise the actual `DEFAULT_MEMBERSHIP_THRESHOLD` boundary

### Correct example (what the TG should produce):

```java
// Test that group node type is preserved after splitting members at threshold
@Test
public void verifyGroupNodeTypes() throws Exception {
    // Setup: create a group with more than DEFAULT_MEMBERSHIP_THRESHOLD members
    // (threshold is 100, so use e.g. 101 members)
    
    // Execute upgrade operation that splits members
    
    // Verify the group node still has primary type "rep:Group"
    // (not incorrectly changed to "rep:MemberReferencesList")
    
    // Verify member reference child nodes exist with type "rep:MemberReferences"
}
```

### Incorrect example (what the TG should avoid):

```java
// BAD: Tests only a group with few members, never hitting the split threshold
@Test
public void testGroupWithFewMembers() {
    // Create group with 5 members — no splitting occurs
    // This test passes even if the split logic is broken
}
```