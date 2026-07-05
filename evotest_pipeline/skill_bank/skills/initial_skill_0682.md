---
name: xml-import-uuid-create-new-validation
description: When testing XML imports with ImportUUIDBehavior.IMPORT_UUID_CREATE_NEW,
  verify that nodes with existing UUIDs are correctly assigned new UUIDs instead of
  causing ItemExistsException. This skill applies to JCR import operations where the
  imported XML contains nodes with UUIDs that already exist in the repository.
code_tags:
- VALIDATION
test_pattern: INTERACTION_TEST
---

# xml-import-uuid-create-new-validation

## Instructions

# XML Import with IMPORT_UUID_CREATE_NEW Validation

## Instructions

- WHEN the TG encounters code that performs XML imports using `ImportUUIDBehavior.IMPORT_UUID_CREATE_NEW` (value `3` from `javax.jcr.ImportUUIDBehavior`)
- THEN the TG should write a test that:
  1. Creates a node in the repository with a specific UUID (e.g., `a84ba01a-cb30-41c7-a5d2-62f03e600001`)
  2. Exports that node (including its subtree) to an XML stream using `session.exportSystemView()`
  3. Imports the same XML back into a different path using `session.importXML()` with `IMPORT_UUID_CREATE_NEW`
  4. Verifies that the import succeeds (i.e., no `ItemExistsException` is thrown)
  5. Verifies that the imported node has a **different UUID** than the original (not the same UUID from the XML)
  6. Verifies the imported node's properties (e.g., stringProp, intProp, mvProp) are correctly set

- Common pitfalls to avoid:
  - **Do NOT** test with `IMPORT_UUID_CREATE_NEW` using XML where the UUID doesn't exist yet — this misses the bug entirely
  - **Do NOT** test only at the `Session` level with `importXML()` without also testing via `Workspace.importXML()` — both paths use the same `ImporterImpl` but may have different setup
  - **Do NOT** forget to call `session.save()` after the import — changes must be persisted before verification
  - **Do NOT** assume that `IMPORT_UUID_CREATE_NEW` simply overwrites — it must generate a new UUID for conflicting nodes
  - **Do NOT** test without verifying the UUID actually changed — the bug is that the importer fails with `ItemExistsException` instead of generating a new UUID

## Example (Correct)

```java
// Create a node with a specific UUID
Node root = session.getRootNode();
Node node = root.addNode("testNode");
node.addMixin("mix:referenceable");
session.save();
String originalUuid = node.getIdentifier();

// Export the node (with its UUID in the XML)
ByteArrayOutputStream out = new ByteArrayOutputStream();
session.exportSystemView("/testNode", out, false, false);

// Create a new parent and do the import
root.addNode("importTarget");
session.save();

session.importXML("/importTarget", 
    new ByteArrayInputStream(out.toByteArray()), 
    ImportUUIDBehavior.IMPORT_UUID_CREATE_NEW);
session.save();

// Verify the imported node exists and has a NEW UUID
Node importedNode = session.getNode("/importTarget/testNode");
assertNotNull(importedNode);
assertNotEquals("UUID should have been reassigned", 
    originalUuid, importedNode.getIdentifier());
assertEquals("stringVal", importedNode.getProperty("stringProp").getString());
```

## Example (Incorrect — misses the bug)

```java
// This test imports XML with a UUID that doesn't exist yet
// It passes even on the buggy version and misses the conflict scenario
String xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
    "<sv:node xmlns:sv=\"http://www.jcp.org/jcr/sv/1.0\" sv:name=\"newNode\">" +
    "<sv:property sv:name=\"jcr:uuid\" sv:type=\"String\">" +
    "<sv:value>new-unique-uuid-0000-0000-000000000000</sv:value>" +
    "</sv:property></sv:node>";

session.importXML("/", new ByteArrayInputStream(xml.getBytes()), 
    ImportUUIDBehavior.IMPORT_UUID_CREATE_NEW);
session.save();
// This passes even on buggy version because the UUID doesn't conflict
```