---
name: xml-model-dump-namespace-prefix-validation
description: WHEN dumping Camel route models to XML, namespace prefixes defined in
  expressions (like XPath) must be excluded from XML output to prevent invalid xmlns:xmlns
  attributes. This skill teaches how to test that dumpModelAsXml produces valid XML
  without namespace prefix leaks.
code_tags:
- TEMPLATE_RESOURCE_LOADING
- NULL_CHECK
- RESOURCE_MANAGEMENT
test_pattern: PARAMETRIC_TEST
---

# xml-model-dump-namespace-prefix-validation

## Instructions

# XML Model Dump Namespace Prefix Validation

## Instructions

WHEN the TG encounters code that calls `ModelHelper.dumpModelAsXml()` (or similar model-to-XML serialization) on a route model containing expressions with namespace prefixes (e.g., XPath expressions in filter/choice nodes like `$body:foo` with `prefix:localname`), THEN the TG should:

1. **Build a route that includes both:**
   - An XPath-based filter expression using a namespace prefix (e.g., `//foo:bar`)
   - A `ChoiceDefinition` with `when` branches also using XPath expressions with namespace prefixes
   - Register namespace prefixes via `org.apache.camel.builder.RouteBuilder` using `namespace()` calls

2. **Call `ModelHelper.dumpModelAsXml()` on the route definition** and verify the resulting XML string:
   - Does NOT contain `xmlns:xmlns` attributes (this is the specific bug pattern — invalid XML)
   - Does contain proper namespace declarations for user-defined prefixes (e.g., `xmlns:foo="http://foo"`)
   - The XML output is well-formed and does NOT cause a `TransformerException` or `SAXParseException` when parsed

3. **Verify that the dumped XML can be parsed back** using standard `javax.xml.parsers.DocumentBuilderFactory` — the buggy version produces invalid XML with `xmlns:xmlns` which fails to parse.

4. **Common pitfalls to avoid:**
   - Testing only the filter node OR only the choice node in isolation — the bug manifests when BOTH are present in the same route
   - Using only xpath() without namespace prefixes — the bug is specifically about namespace prefix handling
   - Forgetting to register namespaces on the RouteBuilder — without namespaces, the bug won't trigger
   - Assuming the XML output is valid without actually parsing it back through a DocumentBuilder

### Correct Test Example:
```java
@Test
public void testDumpModelAsXmlWithChoiceAndFilter() throws Exception {
    RouteBuilder builder = new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .filter().xpath("//foo:bar")
                    .to("mock:filter")
                .end()
                .choice()
                    .when().xpath("//foo:bar")
                        .to("mock:choice")
                .end();
        }
    };
    builder.setNamespaceAware(true);
    builder.getNamespace("foo", "http://foo");
    // ... use ModelHelper.dumpModelAsXml() and verify no xmlns:xmlns
}
```

### Incorrect Test (won't catch the bug):
```java
@Test
public void testDumpModelAsXml() throws Exception {
    // Only tests filter without choice — won't trigger the namespace prefix leak bug
    RouteBuilder builder = new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .filter(xpath("//foo:bar"))
                    .to("mock:filter");
        }
    };
}
```