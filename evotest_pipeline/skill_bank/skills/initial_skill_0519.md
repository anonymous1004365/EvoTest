---
name: merged-branch-visibility-test
description: ''
code_tags:
- CACHE_NULL_RESULT
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# merged-branch-visibility-test

## Instructions

# Merged Branch Visibility Test

## Instructions

**WHEN** the TG encounters code that involves:
- A persistence or storage layer (e.g., `DocumentNodeStore`)
- Branch/merge operations (e.g., `branch`, `merge`)  
- Read operations that follow a merge (`getDocument`, `getNode`, `read`, etc.)

**THEN** the TG should write a test that:

1. **Creates a branch session** from a given persistence context (e.g., `store.createBranchSession()` on a `DocumentNodeStore`).
2. **Writes data** into the branch session (e.g., adds a new document/node).
3. **Merges the branch** back (e.g., `branchSession.merge()` or `store.merge(branchSession, ...)`).
4. **Opens a new, independent read session** (e.g., `store.createSession(...)`) — do NOT reuse the branch session or the original session.
5. **Verifies that the data written in the branch is visible** through the new session (e.g., `assertNotNull(newSession.getNode(path))` or similar).
6. **Expects the test to PASS on the fixed version**. On the buggy version, the test should FAIL — the merged data may not be visible to the new session.

**Common pitfalls to avoid:**
- **Reusing the merged session** for the read check — this can mask visibility bugs because the session may have a cached/pending state. Always create a completely new session/reader after the merge.
- **Only checking the writer's own session** — the bug lies in cross-session visibility, which requires a new reader.
- **Assuming flush/commit is enough** — explicit branch/merge lifecycle must be exercised; a simple write-then-read within the same session will not catch this bug.
- **Forgetting to wait** — if the system is asynchronous, the test may need to wait/poll for visibility. For synchronous systems, the read should be immediate after merge.
- **Testing with the same thread only** — if the system uses thread-local visibility, ensure the new reader runs on a different logical path (e.g., different session object).

**Example (correct approach):**
```java
// Correct: tests that merged branch data is visible to a new reader
DocumentNodeStore store = new DocumentNodeStore(...);
try {
    // Create branch
    DocumentNodeStoreBranch branch = store.createBranchSession();
    String testPath = "/testNode";
    branch.addNode(testPath);
    
    // Merge
    store.merge(branch, null);
    
    // New reader must see the merged data
    Session newSession = store.createSession();
    assertNotNull("Merged branch data must be visible to new readers",
                  newSession.getNode(testPath));
} finally {
    store.dispose();
}
```

**Example (incorrect approach — misses the bug):**
```java
// Incorrect: reuses the same session to read after merge
DocumentNodeStore store = new DocumentNodeStore(...);
DocumentNodeStoreBranch branch = store.createBranchSession();
String testPath = "/testNode";
branch.addNode(testPath);
store.merge(branch, null);

// BUG: This reuses the writer's session, which may have separate visibility
assertNotNull("This might pass even if the data is not globally visible",
              branch.getNode(testPath));
// Also incorrect: doesn't create a new independent reader
```