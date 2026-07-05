---
name: serializable-ctstatement-field-capture
description: When testing serialization of AST elements (like CtStatement), verify
  that all fields including inherited and undocumented ones are properly captured
  during serialization/deserialization. This skill helps catch bugs where field values
  are lost due to incomplete serialization handling.
code_tags:
- SERIALIZATION
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# serializable-ctstatement-field-capture

## Instructions

# Serializable CtStatement Field Capture

## Instructions

- WHEN testing serialization of a Spoon AST element (e.g., CtStatement, CtExpression, CtElement):
  - THEN verify that after serialization+deserialization (round-trip), every field of the original object is preserved in the deserialized copy, including:
    - Fields inherited from parent classes (e.g., CtElement fields like `position`, `metadata`, `comments`, `docComment`, `parent`, etc.)
    - Fields that may not be explicitly set (e.g., `implicit` field in CtStatement, `type` field in CtExpression)
  - Concrete approach:
    1. Create an instance of the AST element using the Spoon factory (e.g., `factory.createLocalVariableDeclaration(...)` for a CtLocalVariable)
    2. Set at least one field that might be lost (e.g., `varDecl.setImplicit(true)` for CtStatement's `implicit` field)
    3. Serialize the element (e.g., write to `ByteArrayOutputStream` via Java `ObjectOutputStream`)
    4. Deserialize back (e.g., read from `ByteArrayInputStream` via Java `ObjectInputStream`)
    5. Assert that the field value is preserved after deserialization (e.g., `assertTrue(deserialized.isImplicit())`)
  - Common mistake: Only checking that the deserialized object is not null or has only basic fields without testing specific non-default field values.
  - When the bug is present, the test should fail because the field `implicit` (or other fields) will return `false` (default) after deserialization, even though it was set to `true` before serialization.

- WHEN a Spoon AST element has a boolean field like `implicit` (or other fields with getter/setter pairs):
  - THEN test that AFTER serialization+deserialization, the getter returns the same value as BEFORE serialization.
  - Example: For `CtStatement`, call `statement.setImplicit(true)` before serialization and `assertTrue(deserializedStatement.isImplicit())` after deserialization.
  - Common mistake: Testing only that the object can be serialized without exceptions, or testing only `equals()` without checking individual field values.

- WHEN you encounter a test that serializes a Spoon AST element:
  - THEN also add a round-trip check for at least one non-default field value to ensure the serialization mechanism captures all fields.
  - Include tests for edge cases: fields set to `true`, fields set to custom objects, etc.