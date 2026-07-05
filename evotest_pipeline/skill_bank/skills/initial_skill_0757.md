---
name: behavior-listener-index-immutability-test
description: Use when testing that IBehaviorListener URL indices remain stable when
  non-listener behaviors are added/removed. Tests must verify that the behavior ID
  assigned to IRequestListener implementations does not shift after unrelated behaviors
  are added or removed from the component.
code_tags:
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# behavior-listener-index-immutability-test

## Instructions

# Behavior Listener Index Immutability on Behavior Removal

## Instructions

WHEN the TG encounters a component that has a list of behaviors (instances of `org.apache.wicket.behavior.Behavior`) where at least one behavior implements `org.apache.wicket.IRequestListener` (which generates an `IBehaviorListener` URL with an index), THEN the TG should test that removing unrelated non-listener behaviors from the component does NOT change the behavior ID (index) assigned to the `IRequestListener` behaviors.

- Create at least one behavior that implements `org.apache.wicket.IRequestListener` (e.g., `LinkBehavior` with `onRequest()`)
- Create several non-listener behaviors (e.g., `AttributeModifier` instances) and add them all to a component
- Start the page with `tester.startPage(page)` and verify the output contains the expected listener index (e.g., `.0`, `.1`)
- Remove some of the non-listener behaviors from the component
- Start the page again and verify that the output STILL contains the same listener index (e.g., `.0` stays `.0`)
- Verify via `component.getBehaviorById(index)` that the same `IRequestListener` instance is still at that index

Common pitfalls to avoid:
- Do NOT assume that removing a behavior earlier in the list shifts listener indices; the framework should preserve them
- Do NOT skip the second `tester.startPage()` call — re-rendering is necessary to regenerate the URL with the current index
- Do NOT test only the case where all behaviors remain; the bug manifests specifically when removal happens and the index unexpectedly changes
- Do NOT forget to implement `IRequestListener` on the test behavior; only `IRequestListener` behaviors get listener indices

**Correct approach:**
```java
@Test
public void urlIndexStabilityAfterRemoval() {
    Behavior link = new LinkBehavior("href");
    Behavior border = new AttributeModifier("class", "border");
    Behavior border2 = new AttributeModifier("class2", "border2");
    
    MyPage page = new MyPage();
    page.getContainer().add(border, link, border2);
    tester.startPage(page);
    
    // link should be at index 0 (first IBehaviorListener)
    assertTrue(tester.getLastResponseAsString().contains(".0"));
    assertEquals(link, page.getContainer().getBehaviorById(0));
    
    // Remove non-listener behaviors
    page.getContainer().remove(border);
    page.getContainer().remove(border2);
    tester.startPage(page);
    
    // link index should STILL be 0
    assertTrue(tester.getLastResponseAsString().contains(".0"));
    assertEquals(link, page.getContainer().getBehaviorById(0));
}
```

**Incorrect approach (would miss the bug):**
```java
@Test
public void urlIndexStabilityAfterRemoval() {
    Behavior link = new LinkBehavior("href");
    MyPage page = new MyPage();
    page.getContainer().add(link);
    tester.startPage(page);
    
    // Only tests a single behavior, no removal scenario
    assertTrue(tester.getLastResponseAsString().contains(".0"));
}
```