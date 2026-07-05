---
name: custom-nodetype-registration-validation
description: When registering custom node types via ReadWriteNodeTypeManager, validate
  that property definition templates with TYPE_UNDEFINED are properly handled (e.g.,
  by setting explicit PropertyType values) to avoid incomplete or non-functional type
  definitions after registration or upgrade.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- TYPE_CONVERSION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# custom-nodetype-registration-validation

## Instructions

# Custom NodeType Registration Validation

## Instructions

- WHEN the TG encounters code that **registers node types** via `ReadWriteNodeTypeManager.registerNodeType(NodeTypeTemplate)` or `ReadWriteNodeTypeManager.registerNodeTypes(NodeTypeTemplate[])` — particularly when the `NodeTypeTemplate` contains **property definition templates** obtained via `getPropertyDefinitionTemplates()`
- THEN the TG should write a **parameteric test** that:
  1. Creates a `NodeTypeTemplate` (e.g. via `ReadWriteNodeTypeManager.createNodeTypeTemplate()`)
  2. Adds a property definition template with **`PropertyType.UNDEFINED`** (e.g. `propDefTemplate.setRequiredType(PropertyType.UNDEFINED)`)
  3. Registers the node type via `registerNodeType(template)`
  4. Retrieves the registered node type via `getNodeType(template.getName())` and **verifies** that the property definition is present and has a non-undefined required type (or that the registration completed without silently dropping/breaking the property definition)
  5. If the node type manager supports it, also test that **`getPropertyDefinitionTemplates()` returns the expected number of entries** (i.e., no property definitions were silently lost after registration)

- **Common pitfalls to avoid:**
  - Testing only with a single hardcoded `PropertyType.STRING` or other non-undefined type — this misses the bug entirely
  - Not retrieving and inspecting the registered node type after `registerNodeType()` to confirm the property definitions were correctly stored
  - Forgetting to call `setName()` on the `NodeTypeTemplate` before registration

- **Expected exception/error on buggy version:** The buggy version may **silently drop** property definitions with `PropertyType.UNDEFINED` from the registered node type, or fail to return them via `getPropertyDefinitionTemplates()`, without throwing any exception. The test should therefore assert that the number of property definitions in the retrieved node type matches expectations, or that the required type of each property definition is not `PropertyType.UNDEFINED`.

**Correct example (what the TG should write):**
```java
@Test
public void testPropertyDefWithUndefinedType() throws Exception {
    ReadWriteNodeTypeManager mgr = ...;
    NodeTypeTemplate ntt = mgr.createNodeTypeTemplate();
    ntt.setName("test:undefinedTypeProperty");
    
    PropertyDefinitionTemplate pdt = mgr.createPropertyDefinitionTemplate();
    pdt.setName("test:property1");
    pdt.setRequiredType(PropertyType.UNDEFINED);
    pdt.setAutoCreated(false);
    pdt.setProtected(false);
    pdt.setMandatory(false);
    pdt.setOnParentVersion(1);
    pdt.setMultiple(false);
    pdt.setAvailableQueryOperators(new String[]{"jcr.operator.equal.to"});
    ntt.getPropertyDefinitionTemplates().add(pdt);
    
    mgr.registerNodeType(ntt);
    
    NodeType registered = mgr.getNodeType("test:undefinedTypeProperty");
    PropertyDefinition[] propDefs = registered.getPropertyDefinitions();
    // Verify property was not silently dropped
    assertTrue("Property definition with UNDEFINED type should be present",
        Arrays.stream(propDefs).anyMatch(pd -> pd.getName().equals("test:property1")));
    // Optionally verify the type was resolved/unchanged
    assertEquals(PropertyType.UNDEFINED, 
        Arrays.stream(propDefs)
            .filter(pd -> pd.getName().equals("test:property1"))
            .findFirst()
            .get()
            .getRequiredType());
}
```

**Incorrect example (what the TG should NOT write — misses the bug):**
```java
@Test
public void testPropertyDefWithStringType() throws Exception {
    ReadWriteNodeTypeManager mgr = ...;
    NodeTypeTemplate ntt = mgr.createNodeTypeTemplate();
    ntt.setName("test:stringTypeProperty");
    PropertyDefinitionTemplate pdt = mgr.createPropertyDefinitionTemplate();
    pdt.setName("test:property1");
    pdt.setRequiredType(PropertyType.STRING);  // BUG: Only STRING, not UNDEFINED
    ntt.getPropertyDefinitionTemplates().add(pdt);
    mgr.registerNodeType(ntt);
    // This passes even on buggy code
}
```