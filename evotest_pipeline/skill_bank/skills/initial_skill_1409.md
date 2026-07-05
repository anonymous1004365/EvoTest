---
name: password-history-import-array-type
description: When importing user data with password history via XML import, the rep:pwdHistory
  property may be stored as a single STRING value instead of a STRINGS array. Test
  that password history properties are always stored as arrays (multi-valued) on import,
  expecting a RepositoryException if single-valued.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# password-history-import-array-type

## Instructions

# Password History Import Array Type Validation

## Instructions

- WHEN the TG encounters code that imports or sets the `rep:pwdHistory` property on a user node during XML import (e.g., via `UserImportHandler`, `UserProvider`, `PasswordHistory`, or any import-related code path)
- THEN the TG should write a test that:
  1. Creates a user with at least one password history entry (e.g., a `rep:pwdHistory` property with a STRING value such as `"{sha1}8efd86fb78a56a5145ed7739dcb00c78581c5375"`)
  2. Exports that user to XML (e.g., via `Session.exportDocumentView` or `Session.exportSystemView`)
  3. Imports the XML back (e.g., via `Session.importXML` with `ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING`)
  4. After import, retrieves the user and checks the `rep:pwdHistory` property — it MUST be multi-valued (i.e., `property.isArray()` returns `true` and `property.getType().isArray()` returns `true`)
  5. Fails with a `RepositoryException` if the property is single-valued (i.e., `isArray()` returns `false`)
- Include concrete values: use password hash strings like `"{sha1}8efd86fb78a56a5145ed7739dcb00c78581c5375"` as the expected history value
- Common pitfalls to avoid:
  - ❌ Testing only the `PasswordHistory` class's `setPasswordHistory` or `updatePasswordHistory` methods in isolation — these may handle array types correctly, while the bug is in the XML import/deserialization path
  - ❌ Testing only the user creation path without XML round-trip — the bug manifests specifically during XML import, not during direct API calls
  - ❌ Assuming that a property set as a single string in XML will automatically be interpreted as an array — without explicit `Type.STRINGS` designation, the import may store it as single-valued
  - ❌ Not checking both `property.isArray()` and `property.getType().isArray()` — both must be true for the property to be properly multi-valued

### Correct Test Pattern Example (Java/JUnit):
```java
// Export user with password history
Session exportSession = adminSession;
String userPath = "/rep:security/rep:authorizables/rep:users/te/testUser";
String xml = exportSession.exportSystemView(userPath, ...);

// Remove and re-import
adminSession.removeItem(userPath);
adminSession.importXML(userPath, new ByteArrayInputStream(xml.getBytes()), ImportUUIDBehavior.IMPORT_UUID_COLLISION_REMOVE_EXISTING);

// Verify the imported property is multi-valued
Tree userTree = adminSession.getRoot().getTree(userPath);
PropertyState pwdHistory = userTree.getProperty("rep:pwdHistory");
assertTrue("rep:pwdHistory must be multi-valued after import", pwdHistory.isArray());
```

### Incorrect Pattern (missing the bug):
```java
// ❌ Only testing the setPasswordHistory method directly — doesn't test XML import
PasswordHistory pwdHistory = new PasswordHistory(...);
pwdHistory.updatePasswordHistory(userTree, ...);
// This works fine, but the bug is in the import path
```