---
name: property-name-case-insensitive-lookup
description: When a configuration property name lookup uses exact case-sensitive matching
  (e.g., Tree.getProperty()) but the user-specified input is case-insensitive (e.g.,
  "PropertyName" vs "propertyName"), the lookup fails silently. This skill teaches
  how to test for this bug by providing property names in different cases and verifying
  they match.
code_tags:
- PROPERTY_NAME_CASE_VALIDATION
test_pattern: PARAMETRIC_TEST
---

# property-name-case-insensitive-lookup

## Instructions

# Property Name Case-Insensitive Lookup

## Instructions

- WHEN the TG encounters code that looks up a property or configuration key by name from a Tree, Node, Map, or similar key-value structure, and the user input for that key is documented or expected to be case-insensitive
- THEN the TG should write a parametric test that:
  1. Sets up the same property/config with one casing (e.g., lowercase like `"propertyName"`)
  2. Looks it up with a different casing (e.g., uppercase like `"PROPERTYNAME"`, mixed case like `"PropertyName"`)
  3. Asserts that the lookup returns the same value as the original casing
  4. The test should expect the buggy version to return `null`, a default value, or throw an exception when the lookup fails due to case mismatch
- Include at least these test cases:
  - **All lowercase input** (e.g., "propertyname")
  - **All uppercase input** (e.g., "PROPERTYNAME")
  - **Mixed case input** (e.g., "PropertyName")
  - **Same case as originally set** (expected to work on both buggy/fixed)
- Common pitfalls:
  - ❌ **Only testing with the exact case** as set in the implementation — this will pass even on the buggy version and miss the bug entirely
  - ❌ **Assuming property name normalization** (e.g., assuming `.toLowerCase()` is called somewhere) — verify by reading the lookup code or by testing multiple cases
  - ❌ **Not testing with null/empty property names** — though the focus is on case, boundary checks on empty strings can also expose issues

### Example (correct approach — this catches the bug)

```java
@Test
public void propertyConfigCaseInsensitive() throws Exception {
    IndexDefinition idx = createIndexDefinition("testIndex", "{\n" +
            "    \"properties\": {\n" +
            "        \"propName\": {\n" +
            "            \"propertyIndex\": true,\n" +
            "            \"type\": \"String\"\n" +
            "        }\n" +
            "    }\n" +
            "}");

    // Lowercase lookup — should work
    assertNotNull("propname", idx.getConfig("propname"));
    
    // Uppercase lookup — should work but fails on buggy
    assertNotNull("PROPNAME", idx.getConfig("PROPNAME"));
    
    // Mixed case — should work but fails on buggy
    assertNotNull("PropName", idx.getConfig("PropName"));
    
    // Original case — works on both
    assertNotNull("propName", idx.getConfig("propName"));
}
```

### Example (incorrect approach — misses the bug)

```java
// ❌ Only tests with the exact same case — passes even on buggy version
@Test
public void propertyConfigExactCase() throws Exception {
    IndexDefinition idx = createIndexDefinition("testIndex", "{\n" +
            "    \"properties\": {\n" +
            "        \"propName\": {\n" +
            "            \"propertyIndex\": true,\n" +
            "            \"type\": \"String\"\n" +
            "        }\n" +
            "    }\n" +
            "}");

    // Only tests the exact case that was configured — never reveals the bug
    assertNotNull("propName", idx.getConfig("propName"));
}
```