---
name: suggestion-update-on-non-index-change
description: When a test relies on a clock-driven periodic scheduler (e.g., suggestion
  index updates that happen on commit after a time interval), the test must verify
  that a non-index commit (a change that does NOT affect the index) still triggers
  the scheduled suggestion refresh. This skill covers testing with node adds/removes
  after the suggestion update frequency has elapsed.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# suggestion-update-on-non-index-change

## Instructions

# Suggestion Update on Non-Index Change

## Instructions

- WHEN the TG encounters an `IndexDefinition` with a `DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES` (configuration that controls how often suggestions are rebuilt) AND the code has a static `Clock` (e.g., `LuceneIndexEditorContext.setClock(clock)`) used to control time in tests:

  - THEN the TG should write a test that:
    1. Creates an index definition that has `useInSuggest` set to `true` on a property
    2. Adds at least one node that matches the indexed node type (e.g., `nt:unstructured`) so suggestions exist
    3. Commits to persist the indexed content via `root.commit()`
    4. Advances the `clock` past `DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES` (e.g., `clock.waitUntil(clock.getTime() + TimeUnit.MINUTES.toMillis(IndexDefinition.DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES))`)
    5. **Adds a node that does NOT match the indexed node type** (e.g., using `"oak:Unstructured"` instead of `"nt:unstructured"`) — a change that causes no index modification
    6. Commits the non-index change via `root.commit()`
    7. Runs a suggestion query (e.g., `"SELECT [rep:suggest()] as suggestion... WHERE suggest('...')"`)
    8. Asserts that the suggestion result is non-empty (e.g., `assertEquals(1, suggestions.size())`)

  - The expected behavior on the fixed version: the non-index commit after the frequency interval **does** trigger the suggestion refresh, so suggestions appear.
  - The expected behavior on the buggy version: the non-index commit does **not** trigger suggestion refresh, so `suggestions.size()` returns `0` and the test fails with `expected:<1> but was:<0>`.

  - The TG should verify suggestions appear even when:
    - The change that caused the commit does not modify any index-relevant property or node type
    - The suggestion update frequency has elapsed since the last suggestion rebuild

  - Common pitfalls to avoid:
    - ❌ Only adding nodes that match the indexed type — that would not exercise the non-index-change path
    - ❌ Forgetting to advance the `clock` past `DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES` — without this, the suggestion update is not scheduled
    - ❌ Forgetting to set the clock on `LuceneIndexEditorContext` via `setClock()` — the test requires a virtual clock to control time
    - ❌ Using a real `Clock` or failing to reset it in `@After` — static state can leak across tests
    - ❌ Only testing that a change to an indexed property/type triggers the suggestion update — the bug is specifically about a non-index change failing to trigger it

  - **Correct example:**
    ```java
    // Add an indexed node
    root.getTree("/").addChild("indexedNode")
        .setProperty(JcrConstants.JCR_PRIMARYTYPE, nodeType, Type.NAME);
    root.commit();

    // Advance time past the update frequency
    clock.waitUntil(clock.getTime() + TimeUnit.MINUTES.toMillis(
        IndexDefinition.DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES));
    clock.getTime(); // get one more tick

    // Add a node that does NOT match the indexed type
    root.getTree("/").addChild("some-non-index-change")
        .setProperty(JcrConstants.JCR_PRIMARYTYPE, "oak:Unstructured", Type.NAME);
    root.commit();

    // Suggestions should now be updated
    Set<String> suggestions = getSuggestions(nodeType, "indexedn");
    assertEquals(1, suggestions.size());
    ```

  - **Incorrect example (missing non-index change):**
    ```java
    root.getTree("/").addChild("indexedNode")
        .setProperty(JcrConstants.JCR_PRIMARYTYPE, nodeType, Type.NAME);
    root.commit();
    clock.waitUntil(clock.getTime() + TimeUnit.MINUTES.toMillis(
        IndexDefinition.DEFAULT_SUGGESTER_UPDATE_FREQUENCY_MINUTES));
    clock.getTime();
    // Missing: a commit after the interval that makes no index change
    Set<String> suggestions = getSuggestions(nodeType, "indexedn");
    assertEquals(1, suggestions.size()); // FAILS — suggestions not refreshed
    ```