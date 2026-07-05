---
name: principal-namehint-like-pattern-search
description: When searching for principals using a name hint via LIKE queries, tests
  must verify that exact principal names are found even when the name hint matches
  the principal name directly. This skill teaches how to test principal lookups that
  use SQL LIKE patterns with wildcards.
code_tags:
- RESOURCE_MANAGEMENT
- VALIDATION
- EDGE_CASE_INPUT
- STRING_MATCHING_HINT
test_pattern: STATE_TEST
---

# principal-namehint-like-pattern-search

## Instructions

# Principal Name Hint LIKE Pattern Search

## Instructions

WHEN the TG encounters code that searches for principals (e.g., via `findPrincipals` or `getPrincipal`) using a name hint that is built into a LIKE query pattern (e.g., prepending `%` to form `'%nameHint'`),

THEN the TG should write a test that:

1. Creates a test user/principal with a specific known principal name (e.g., `"TestUser"`).
2. Calls `findPrincipals(principalNameHint, searchType)` where `principalNameHint` is the exact name of the created principal (e.g., `"TestUser"`).
3. Verifies that the returned iterator contains a principal whose name equals the exact expected principal name — **not just a partial match**.
4. Verifies, specifically, that the principal returned by `getPrincipal(principalNameHint)` is **non-null** and matches the expected principal name.

Common pitfalls to avoid:
- Testing only with name hints that contain special characters or wildcards (e.g., `"*"`, `"?"`, `"%"`) — this hides the bug because the LIKE pattern may accidentally match.
- Assuming that if the name hint is a substring of the principal name, the search will automatically work — the LIKE pattern may fail when the name hint is the **full exact name** due to the wildcard prefix logic.
- Testing only the `findPrincipals` method without also testing `getPrincipal` with the same name hint — both methods may be affected differently.
- Forgetting to register the test user/principal before attempting to search for it.

### Correct Example (catches the bug):
```java
// Create a user with a known principal name
String userId = adminSession.getUserManager().createUser("TestUser", "pw").getPrincipal().getName();
adminSession.save();

// Search by exact name hint — this should find the principal
Iterator<? extends Principal> result = principalProvider.findPrincipals("TestUser", PrincipalProvider.SEARCH_TYPE_ALL);
assertTrue("Expected principal to be found by name hint TestUser", result.hasNext());
Principal found = result.next();
assertEquals("TestUser", found.getName());

// Also verify getPrincipal works with exact name hint
Principal p = principalProvider.getPrincipal("TestUser");
assertNotNull("Expected principal to be found", p);
assertEquals("TestUser", p.getName());
```

### Incorrect Example (misses the bug):
```java
// Only testing with partial name hints that happen to work with the LIKE pattern
String userId = adminSession.getUserManager().createUser("TestUser123", "pw").getPrincipal().getName();
adminSession.save();

Iterator<? extends Principal> result = principalProvider.findPrincipals("Test", PrincipalProvider.SEARCH_TYPE_ALL);
assertTrue(result.hasNext());
// This passes even if exact-match lookup is broken
```