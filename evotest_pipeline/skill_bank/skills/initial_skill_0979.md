---
name: xml-schema-encoding-resolution
description: When validating XML schemas that include/import other schemas with non-UTF-8
  encodings, the resource resolver must properly propagate the encoding declaration
  from the referenced XSD. This skill helps tests detect when the LSResourceResolver
  fails to use the declared encoding (e.g., ISO-8859-1) and falls back to UTF-8, causing
  encoding errors.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- VALIDATION
- RESOURCE_MANAGEMENT
- XML_ENCODING_RESOLUTION
test_pattern: INTERACTION_TEST
---

# xml-schema-encoding-resolution

## Instructions

# XML Schema Include Encoding Resolution

## Instructions

- WHEN the TG encounters a `DefaultLSResourceResolver` or custom `LSResourceResolver` that resolves included/imported XML schemas (XSD files) during document validation, AND at least one of those schemas declares a non-UTF-8 encoding (e.g., `<?xml version="1.0" encoding="ISO-8859-1"?>`)
- THEN the TG should write an **interaction test** that:
  1. Creates a main XSD that includes/imports another XSD with a non-UTF-8 encoding
  2. Sends a valid XML message containing characters that differ between UTF-8 and the declared encoding (e.g., accented characters like `é` which is `&#233;` in ISO-8859-1)
  3. Verifies that validation succeeds without any `CamelExecutionException` or SAX parse exception
  4. Specifically tests that the `resolveResource` method in the `LSResourceResolver` produces an `LSInput` whose encoding is correctly set to match the included schema's declared encoding (not falling back to null/UTF-8)

- **What to verify**: The test should pass on the **fixed** version and fail (throw an exception) on the **buggy** version where the encoding is not propagated.

- **Common pitfalls to avoid**:
  - Testing only with UTF-8 encoded schemas — the bug only manifests with non-UTF-8 encodings
  - Using only simple ASCII content in test XML messages — accented/special characters are needed to trigger encoding issues
  - Assuming that setting the `encoding` property on the `InputSource` is sufficient — the `LSInput`'s encoding must be explicitly set from the XSD's XML declaration
  - Testing only the resolver in isolation without actually performing schema validation — the encoding bug only surfaces during real validation

- **Example (correct test approach)**:
```java
// Create XSD files with ISO-8859-1 encoding
// sentence.xsd: <?xml version="1.0" encoding="ISO-8859-1"?> containing accented chars
// text.xsd: includes sentence.xsd via xs:include
// Send XML with: <text>&#233; is the letter e with acute</text>
// Assert validation completes without error
```

- **Example (incorrect test approach)**:
```java
// Tests with UTF-8 schemas only — will pass on buggy version too
// Uses only ASCII text — no encoding-dependent characters
// Does not actually validate XML against schemas
```