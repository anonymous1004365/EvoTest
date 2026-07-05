---
name: distribution-management-relocation-inheritance
description: When inheriting properties from a parent object graph into a child object
  that already has a partially-populated instance, each field must be individually
  checked and inherited. This skill teaches verifying that all Sub-fields are correctly
  inherited during deep merge operations.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- OBJECT_GRAPH_DEEP_MERGE
test_pattern: STATE_TEST
---

# distribution-management-relocation-inheritance

## Instructions

# Distribution Management Relocation Inheritance

## Instructions

- WHEN the TG encounters a method that performs deep merge/copy of fields from a parent object to a child object (e.g., `assembleDistributionManagementInheritance(Model child, Model parent)`), where the child may already have a `DistributionManagement` instance and the method conditionally sets each individual field
- THEN the TG should write a test that:
  1. Creates a parent `Model` with a fully-populated `DistributionManagement` object containing ALL fields set (e.g., `repository`, `snapshotRepository`, `downloadUrl`, `relocation`, `site`, `status`)
  2. Creates a child `Model` with a **non-null** but empty `DistributionManagement` object (i.e., `new DistributionManagement()` with no field values set)
  3. Calls `assembleModelInheritance(child, parent)`
  4. Asserts that **each individual inherited field** is correctly propagated from parent to child, including nested objects like `Relocation` via `setRelocation()`, `Site` via `setSite()`, `DeploymentRepository` instances via `setRepository()`/`setSnapshotRepository()`, and `String` fields like `downloadUrl`
  5. Also asserts that fields explicitly marked as NOT inherited (e.g., `status`) remain `null` on the child

- Common pitfalls:
  - **Testing only the top-level object**: Do NOT just test that `child.getDistributionManagement()` is non-null. The bug was that `Relocation` inheritance `if (cDistMgmt.getRelocation() == null) { cDistMgmt.setRelocation(pDistMgmt.getRelocation()); }` was **missing entirely** from the buggy version. You must verify each nested sub-field individually.
  - **Testing with child having null DistributionManagement**: When `child.getDistributionManagement()` is null, the parent object is assigned wholesale — this masks the bug. The bug only appears when the child already has a DistributionManagement instance.
  - **Forgetting to initialize child's DistributionManagement**: If the test doesn't call `child.setDistributionManagement(new DistributionManagement())`, the child's DM will be null and the entire parent DM will be assigned, which doesn't test the per-field inheritance logic.

- Correct example:
```java
Model parent = makeBaseModel("parent");
Model child = makeBaseModel("child");

DistributionManagement parentDM = new DistributionManagement();
parentDM.setDownloadUrl("downloadUrl");
parentDM.setRelocation(new Relocation());  // this was missing from inheritance
parentDM.setStatus("deployed");  // should NOT be inherited
// ... set repository, snapshotRepository, site, etc.
parent.setDistributionManagement(parentDM);

child.setDistributionManagement(new DistributionManagement()); // child has empty DM

assembler.assembleModelInheritance(child, parent);

DistributionManagement childDM = child.getDistributionManagement();
assertNotNull("Check distMgmt inherited", childDM);
assertNull("Check relocation NOT inherited", childDM.getRelocation());  // BUG: this assertion FAILS on buggy version
assertNull("Check status NOT inherited", childDM.getStatus());
assertEquals("Check downloadUrl inherited", parentDM.getDownloadUrl(), childDM.getDownloadUrl());
```

- Incorrect example (would not catch the bug):
```java
// Child has no DistributionManagement at all - entire parent object is assigned
Model child = makeBaseModel("child");
// No child.setDistributionManagement(...) call
assembler.assembleModelInheritance(child, parent);
assertNotNull(child.getDistributionManagement()); // passes even with the bug
```