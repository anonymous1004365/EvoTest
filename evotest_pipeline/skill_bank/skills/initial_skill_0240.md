---
name: missing-property-removal-throws-pathnotfound
description: WHEN calling Node.setProperty with a null value to remove a property
  that does not exist on the node, the test must verify the correct exception type
  (PathNotFoundException) rather than assuming silent success or a different exception.
  Test the bug where NodeDelegate.setProperty fails to check if the property exists
  before trying to remove it, leading to a missing property removal.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# missing-property-removal-throws-pathnotfound

## Instructions

# Missing Property Removal Throws PathNotFoundException

## Instructions

- WHEN the TG encounters test code that calls `Node.setProperty(propertyName, (T) null)` or `node.getProperty(propertyName).remove()` on a JCR `Node` or `Session` object, where the property might not exist on the node
- THEN the TG should write a test that:
  1. Checks the property does NOT exist on the node (hasProperty returns false)
  2. Calls `setProperty("missingProperty", (String) null)` or an equivalent null-valued removal API call
  3. Asserts that a `javax.jcr.PathNotFoundException` is thrown from the removal call, with a message containing the missing property name (e.g., `"missing"`)
- Common pitfalls to avoid:
  - Do NOT assume that removing a non-existent property silently succeeds — JCR API requires `PathNotFoundException`
  - Do NOT test only the case where the property exists before removal (happy path) — this bug specifically occurs when the property does NOT exist and `remove()` is triggered via `setProperty(null)`
  - Do NOT catch the exception generically — assert the exact exception type and message content

**Correct example:**
```java
@Test
public void testRemoveMissingProperty() throws RepositoryException {
    Session session = getAdminSession();
    Node root = session.getRootNode();
    // Ensure property does NOT exist
    assertFalse("property 'missing' should not exist before test", root.hasProperty("missing"));
    try {
        root.setProperty("missing", (String) null);
        fail("Expected PathNotFoundException");
    } catch (PathNotFoundException e) {
        assertTrue(e.getMessage().contains("missing"));
    }
}
```

**Incorrect example (does not catch the bug):**
```java
@Test
public void testRemoveMissingProperty() throws RepositoryException {
    Session session = getAdminSession();
    Node root = session.getRootNode();
    // Does not check pre-condition, assumes property may or may not exist
    root.setProperty("missing", (String) null);  // Silently passes on buggy version, should throw
}
```