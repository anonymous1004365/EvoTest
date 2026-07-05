---
name: xpath-facet-query-sql2-conversion
description: When XPath queries use rep:facet(property) to extract facet properties,
  the XPathToSQL2Converter must correctly convert them to SQL-2 format, and tests
  should validate that facet property references in XPath (especially nested relative
  paths like jcr:data/jcr:createdBy) produce the expected SQL-2 output. Use this skill
  when testing XPath query conversion involving facet extraction.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- CONCURRENCY
- STATE_MUTATION
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# xpath-facet-query-sql2-conversion

## Instructions

# XPath rep:facet Query Conversion to SQL-2

## Instructions

- WHEN the TG encounters a class that converts XPath queries to SQL-2 (e.g., `XPathToSQL2Converter`) and the conversion logic handles `rep:facet(property)` expressions  
  - THEN the TG should write a parametric test that feeds various XPath facet queries into the converter and verifies the generated SQL-2 statement matches expected output  
  - Include test cases where the facet property is a simple name (e.g., `rep:facet(jcr:createdBy)`) AND where it is a nested relative path (e.g., `rep:facet(jcr:data/jcr:createdBy)`)  
  - Verify that the converter produces correct SQL-2 like `select [jcr:path], [jcr:score], [rep:facet(jcr:data/jcr:createdBy)]` from the XPath input  

- WHEN the TG writes a test that validates XPath facet conversion  
  - THEN the TG should compare the actual output SQL-2 string with the expected SQL-2 string using `assertEquals`  
  - The test should parse the XPath expression into the AST model, invoke the converter, and check that the `toString()` of the result matches the expected SQL-2 query  

- Common pitfalls to avoid:  
  - Testing only simple facet property names and missing nested relative path cases (like `jcr:data/jcr:createdBy`)  
  - Assuming facet property paths cannot contain `/` separators (they can, and the converter must preserve the full path)  
  - Failing to include both `jcr:path` and `jcr:score` in the expected SELECT clause of the SQL-2 output  
  - Using raw string comparison without normalizing whitespace or ensuring the full SELECT statement structure is verified  

- Example correct test approach:  
  ```java
  @Test
  public void testFacetConversionXPath() throws Exception {
      String xpath = "/jcr:root//*/(rep:facet(jcr:data/jcr:createdBy))";
      String expectedSql = "select [jcr:path], [jcr:score], [rep:facet(jcr:data/jcr:createdBy)]";
      
      XPathToSQL2Converter converter = new XPathToSQL2Converter();
      String result = converter.convert(xpath);
      
      assertEquals(expectedSql, result);
  }
  ```

- Example test approach that would MISS the bug:  
  ```java
  // BAD: Only tests simple facet property names
  @Test
  public void testSimpleFacetConversionXPath() throws Exception {
      String xpath = "/jcr:root//*/(rep:facet(jcr:createdBy))";
      String expectedSql = "select [jcr:path], [jcr:score], [rep:facet(jcr:createdBy)]";
      
      XPathToSQL2Converter converter = new XPathToSQL2Converter();
      String result = converter.convert(xpath);
      
      assertEquals(expectedSql, result);
  }
  // This test passes even when the code fails to correctly convert nested paths like jcr:data/jcr:createdBy
  ```