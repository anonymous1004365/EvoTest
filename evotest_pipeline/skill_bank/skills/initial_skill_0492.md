---
name: fragment-markup-id-collision
description: When a Panel contains a Fragment whose wicket:id matches a regular child
  Component's id in the same panel markup, the FragmentMarkupSourcingStrategy may
  resolve the wrong markup stream. This skill teaches how to test that Fragment markup
  sourcing correctly selects the fragment definition even when a component with the
  same id exists.
code_tags:
- STATE_MUTATION_FLAG
- IDENTITY_COMPARISON
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# fragment-markup-id-collision

## Instructions

# Fragment Markup Sourcing Strategy with Duplicate IDs

## Instructions

WHEN the code under test involves a `Fragment` component that is attached to a parent `Panel` or `MarkupContainer`, AND the panel markup contains both:
1. A child `Component` (e.g., a `<div wicket:id="X">`) with a specific `wicket:id`
2. A `<wicket:fragment wicket:id="X">` definition with the **same** `wicket:id`

THEN the TG MUST write a test that:
- Creates the parent Panel (or MarkupContainer) that contains both the component with id `"X"` and the fragment definition with id `"X"` in its markup
- Adds a `Fragment` component with the same id `"X"` to the panel
- Renders the page/panel (e.g., using a `WicketTester`)
- Verifies that the rendered HTML contains the **fragment body content** (i.e., `"fragment body"`), NOT the content from the non-fragment child component with the same id
- Expects that without the fix, the `FragmentMarkupSourcingStrategy` resolves the wrong markup stream (the parent component's markup instead of the fragment definition's markup), causing incorrect rendering

**Common pitfalls:**
- Testing only with unique IDs and never testing the case where a component ID collides with a fragment ID in the same panel markup
- Assuming `FragmentMarkupSourcingStrategy.getMarkup()` always returns the correct `<wicket:fragment>` markup without testing the ID collision scenario
- Not testing that the rendered output actually contains the expected fragment content vs. the parent component's content
- Testing with `Fragment` directly as a standalone component rather than embedded inside a `Panel` that has both a regular component and a fragment with the same id

**Correct test pattern (Java/Wicket):**
```java
@Test
public void testComponentAndFragmentWithSameId() {
    FragmentTestPanel_2 panel = new FragmentTestPanel_2("testPanel");
    Page page = new PageWithPanel(panel);
    tester.startPage(page);
    
    // The fragment body should be rendered, not the panel's child component content
    String rendered = tester.getLastResponseAsString();
    assertThat("Fragment content should be present", rendered, containsString("fragment body"));
    
    // Additionally, the panel's own component with same id should render separately
    assertThat("Panel component with same id should also be present", rendered, containsString("[same id as fragment below]"));
}
```

**Incorrect test pattern:**
```java
// BAD: Only tests with unique IDs, missing the collision scenario
@Test
public void testFragmentRendering() {
    Fragment fragment = new Fragment("uniqueId", "testFrag", this);
    add(fragment);
    // No collision, so the bug would not be triggered
}
```