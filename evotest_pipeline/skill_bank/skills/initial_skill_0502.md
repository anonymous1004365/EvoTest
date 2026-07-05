---
name: uuid-collision-import-same-tree
description: When importing XML with a UUID collision where the import target path
  overlaps with the existing node (same tree), REMOVE_EXISTING behavior should throw
  a ConstraintViolationException because removing the existing node would also remove
  the import target. Tests must verify this exception is thrown.
code_tags:
- UUID_COLLISION_IMPORT
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# uuid-collision-import-same-tree

## Instructions

# UUID Collision Import — Same Tree Removal Exception

## Instructions

- **WHEN** the TG encounters an XML import operation with `ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING` where the import target path (`destAbsPath`) is an ancestor of, or the same as, the path of the node whose UUID is being collided with (i.e., importing onto the same tree)
- **THEN** the TG should write a test that expects `javax.jcr.nodetype.ConstraintViolationException` to be thrown, because removing the existing conflicting node would also remove the import target node itself, creating an impossible operation. The test should:
  1. Create a referenceable node (add `mix:referenceable` mixin) at a path, get its UUID
  2. Export that node's subtree to an XML stream using `superuser.exportSystemView(path, out, true, false)`
  3. Import the XML stream back into the **same** path using `ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING`
  4. Wrap the import call in a try-catch for `ConstraintViolationException`, calling `fail("ConstraintViolationException expected")` before the import and catching the exception in the catch block
  5. **Do NOT** call `superuser.save()` before the import — the bug specifically occurs with transient (unsaved) state

- **WHEN** the TG encounters `IMPORT_UUID_COLLISION_REMOVE_EXISTING` with an import target path **different** from the colliding node's path (e.g., importing a colliding node under a sibling), then a `ConstraintViolationException` should **NOT** be thrown — the existing node should simply be removed and the import should succeed. Verify the original node no longer exists and the new node exists under the target.

- **Common pitfalls to avoid:**
  - Do NOT test only saved state (`superuser.save()` before import) — the bug manifests with transient (unsaved) nodes. Test both saved and transient scenarios separately.
  - Do NOT forget to call `fail("ConstraintViolationException expected")` before the import call — this is essential to make the test fail if no exception is thrown.
  - Do NOT use `IMPORT_UUID_COLLISION_REPLACE_EXISTING` when testing for the exception — the behavior differs per collision mode. Only `REMOVE_EXISTING` should throw for same-tree collisions.
  - Do NOT test `IMPORT_UUID_COLLISION_CREATE_NEW` or `IMPORT_UUID_COLLISION_THROW` in this same-tree scenario — they have different expected behaviors (CREATE_NEW succeeds with new UUID; THROW throws `ItemExistsException`).

### Correct Example (from actual bug test):
```java
public void testTransientRemoveUUIDSameTree() throws Exception {
    try {
        superuser.importXML(path, getImportStream(), ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING);
        fail("ConstraintViolationException expected");
    } catch (ConstraintViolationException e) {
        // success
    }
}
```

### Incorrect Example (missing fail() call, no exception assertion):
```java
public void testTransientRemoveUUIDSameTree() throws Exception {
    // BAD: no fail() call before, so if no exception is thrown the test silently passes
    superuser.importXML(path, getImportStream(), ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING);
}
```