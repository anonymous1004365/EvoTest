---
name: lucene-index-time-boost-relative-property
description: When testing Lucene property index queries that involve index-time field
  boosts in combination with relative property value scoring, the TG should verify
  that all matching nodes are returned in the correct boosted order, not just a single
  node. This skill catches bugs where relative property scoring inadvertently filters
  out or skips nodes during query evaluation.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
test_pattern: STATE_TEST
---

# lucene-index-time-boost-relative-property

## Instructions

# Lucene Index-Time Field Boost And Relative Property Scoring

## Instructions

- WHEN the TG encounters a Lucene property index query that uses **index-time field boosting** (`@boost` in index definition) combined with a **relative property** (`@propertyRelative` in index definition) that points to a node-relative property for dynamic scoring:
  - THEN the TG should write a test that creates **multiple nodes under the same parent**, each with **different values for the relative property**, and verify that **all nodes are returned** in the correct boosted order, not just a single node.
  - The test must assert the **exact ordered list of paths** in the query result (e.g., using `assertEquals(expectedPaths, actualPaths)`), where the order reflects the combined effect of static field boost and dynamic relative property scoring.

- Common pitfalls:
  - **Testing with only one matching node**: A single-node test will pass even if the relative property logic incorrectly filters out other nodes.
  - **Testing only static boost without relative property**: The bug manifests specifically when both `@boost` AND `@propertyRelative` are set in the index definition.
  - **Ignoring the index definition**: The test must explicitly define and register a Lucene index definition that includes both `@boost` and `@propertyRelative` for the same property.
  - **Asserting only that results contain expected nodes** (using `assertContains`): Use `assertEquals` on the **ordered list** of paths, since boosting is about ordering, not just presence.

- Example of a correct test (Java/JUnit 4):

  ```java
  @Test
  public void indexTimeFieldBoostAndRelativeProperty() throws Exception {
      // Register index definition with field boost AND relative property
      // Index: /test content with property 'foo'
      //   - @boost=2.0 for 'foo'
      //   - @propertyRelative=bar (relative property on each node for dynamic scoring)
  
      // Create multiple nodes with different 'bar' values
      //   /test/a  bar=1  (score = 2.0 * 1 = 2.0)
      //   /test/b  bar=4  (score = 2.0 * 4 = 8.0)  ← highest
      //   /test/c  bar=2  (score = 2.0 * 2 = 4.0)
  
      // Query: //element(*, nt:base)[@foo = 'value']
      // Expected order: /test/b (highest score), /test/c, /test/a (lowest score)
      List<String> result = query("//element(*, nt:base)[@foo = 'value']");
      assertEquals(
          Arrays.asList("/test/b", "/test/c", "/test/a"),
          result
      );
  }
  ```

- Example of an incorrect test that would NOT catch the bug:

  ```java
  // BAD: Only 1 node — won't catch filtering issues
  @Test
  public void indexTimeFieldBoostAndRelativeProperty() throws Exception {
      // Create only /test/a with bar=1
      List<String> result = query("//element(*, nt:base)[@foo = 'value']");
      assertEquals(Arrays.asList("/test/a"), result); // passes even if buggy
  }
  ```

- Verify that the test would **fail on the buggy version** and **pass on the fixed version**.