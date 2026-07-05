---
name: page-window-manager-remove-obsolete
description: When testing a window-based page manager's `removeObsoleteIndices` method
  that uses a sliding window with index tracking, the TG should test that adding multiple
  pages and then removing obsolete entries correctly evicts the earliest page(s) when
  the window capacity is exceeded.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# page-window-manager-remove-obsolete

## Instructions

# Page Window Manager: Remove Obsolete Indices After Window Overflow

## Instructions

- WHEN the TG encounters a `PageWindowManager` or similar class that maintains a sliding window of page indices (via methods like `createPageWindow(pageId, windowSize)` and `removeObsoleteIndices(windowSize)`)
- THEN the TG should write a test that:
  1. Creates a manager instance
  2. Calls `createPageWindow(page0id, windowSize)` for page 0
  3. Calls `createPageWindow(page1id, windowSize)` for page 1 — this should cause page 0 to become obsolete (since the manager tracks indices in order and only keeps `windowSize` entries)
  4. Calls `removeObsoleteIndices(windowSize)` 
  5. Verifies that page 0's entry is removed (e.g., by asserting that `getPageWindow(page0id)` returns `null` or that the session no longer contains page 0)
  6. Verifies that page 1's entry is still present (e.g., by asserting that `getPageWindow(page1id)` returns the expected entry)

- **Common pitfalls**: 
  - Testing with only a single page and verifying it is NOT removed — this does not exercise the overflow/eviction behavior
  - Assuming `removeObsoleteIndices` is a no-op or cleanup-only method that never removes entries
  - Forgetting that the window index tracking is sequential: adding page N+1 after page N should make page N obsolete if the window size is 1
  - Not testing internal state (index tracking) — the test should verify both the presence of newer entries AND the absence of evicted entries

- **Example** (correct):
```java
@Test
public void removeObsoleteIndices() {
    PageWindowManager manager = new PageWindowManager();
    int maxSize = 1;
    int page0id = 0;
    int page1id = 1;
    
    manager.createPageWindow(page0id, maxSize);
    manager.createPageWindow(page1id, maxSize); // page0 becomes obsolete
    manager.removeObsoleteIndices(maxSize);
    
    assertNull("Page0 must be lost when Page1 has been added", manager.getPageWindow(page0id));
    assertNotNull("Page1 must still exist", manager.getPageWindow(page1id));
}
```

- **Example** (incorrect):
```java
@Test
public void removeObsoleteIndices() {
    PageWindowManager manager = new PageWindowManager();
    manager.createPageWindow(0, 5);
    manager.removeObsoleteIndices(5);
    // only tests that a single page is NOT removed — window is not full
    assertNotNull(manager.getPageWindow(0));
}
```