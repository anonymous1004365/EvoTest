---
name: suggest-query-acl-filtering
description: When testing suggestion queries on a Lucene index with access control
  restrictions, the TG must verify that suggest results respect user permissions.
  The failure message "There should be some suggestion" indicates the suggest feature
  returns no results when it should. Tests must ensure the suggest index is populated
  and queryable under access-controlled content.
code_tags:
- ACCESS_CONTROL_EVALUATION
test_pattern: STATE_TEST
---

# suggest-query-acl-filtering

## Instructions

# Suggest Query Access Control Filtering

## Instructions

- WHEN the TG encounters a test for Lucene suggestion queries (`jcr:contains(...)` or `rep:suggest()` with access control restrictions on the indexed content:
  - THEN it should create a suggest index with `useInSuggest=true` on a property (e.g., `jcr:title`), populate the index with nodes that have indexed content, set up access control (ACL) entries that grant the test user `jcr:read` permission on some nodes but restrict access to others, and query the suggest endpoint — verifying that suggestions are returned for accessible content.
  - Include concrete path setup: e.g., create a privileged node at `/content/public` with a child node containing `jcr:title="french` and a restricted node at `/content/private` with a child node containing `jcr:title="fries"`. Apply an ACL that denies `jcr:read` on `/content/private` for the test user but grants it on `/content/public`. Then set the test user's session and assert that a suggestion query for "fr" returns accessible results (e.g., the "french" node's title) but not the restricted ones, OR that suggestions still exist when accessible content is present.
  - Common pitfalls:
    - Testing suggestion queries without setting up any indexed content, leading to zero suggestions despite the test expecting results.
    - Forgetting to commit changes to the `oak:index` node after adding the suggest index definition.
    - Not setting the user session or incorrectly applying ACL permissions (e.g., denying read on both public and private paths).
    - Assuming the suggest index is available via `rep:suggest()` without properly configuring `suggestAnalyzed=true` on the indexed property.
    - Not using `refresh()` on the session after ACL changes.

- Correct example:
```java
// Setup suggest index with useInSuggest=true
Node index = root.getTree("/oak:index/mySuggestIndex");
Node propNode = index.addNode("indexRules", "nt:unstructured")
    .addNode("nt:base", "nt:unstructured")
    .addNode("properties", "nt:unstructured");
Node prop = propNode.addNode("title", "nt:unstructured");
prop.setProperty("propertyIndex", true);
prop.setProperty("useInSuggest", true);
prop.setProperty("suggestAnalyzed", true);

// Add content accessible to test user
Node accessible = root.getTree("/content/public");
Node accessibleChild = accessible.addNode("node1", "nt:unstructured");
accessibleChild.setProperty("jcr:title", "french fries");

// Deny test user on private content
Node denied = root.getTree("/content/private");
// Grant testUser read on public, deny on private via ACL
// ... setup ACL entries ...

// Test suggestion query as testUser
adminSession.refresh();
Session testSession = login(testUser);
QueryManager qm = testSession.getWorkspace().getQueryManager();
String sql2 = "SELECT [rep:suggest()] FROM [nt:base] WHERE suggest('fr')";
Query q = qm.createQuery(sql2, Query.JCR_SQL2);
QueryResult result = q.execute();
Row[] rows = result.getRows();
assertTrue("There should be some suggestion", rows.length > 0);
```

- Incorrect example (would miss the bug):
```java
// ❌ Wrong: No content indexed, no access control setup
Node index = ...; // setup index but no data
Session testSession = login(testUser);
QueryManager qm = testSession.getWorkspace().getQueryManager();
String sql2 = "SELECT [rep:suggest()] FROM [nt:base] WHERE suggest('fr')";
QueryResult result = qm.createQuery(sql2, Query.JCR_SQL2).execute();
assertEquals("Should return 0 suggestions", 0, result.getRows().length);
// This passes trivially but never tests whether suggest works with access control
```