---
name: output-transformer-container-markup-resource-verification
description: When verifying markup resources for output transformer containers that
  may not have their own markup but delegate to children, ensure tests verify that
  the container does not incorrectly search for non-existent associated markup files.
  Use when testing AbstractOutputTransformerContainer subclasses or components with
  transformer behaviors.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- EXCEPTION_HANDLING
- COMPONENT_LIFECYCLE
- RESOURCE_LOADING
test_pattern: INTERACTION_TEST
---

# output-transformer-container-markup-resource-verification

## Instructions

# Output Transformer Container Markup Resource Verification

## Instructions

### WHEN the TG encounters:
- A subclass of `AbstractOutputTransformerContainer` (e.g., `NoopOutputTransformerContainer`) or any component that uses `AbstractTransformerBehavior`
- A component that transforms or delegates its output rather than rendering its own markup
- A page or test that nests such a container and checks rendering of its children

### THEN the TG should:
1. **Test that the container does NOT fail with "Unable to find associated markup file"** when:
   - The container is placed on a page that has child components with their own markup (e.g., a `Border` with `wicket:id="myBorder"`)
   - The container's `renderHead()` method is invoked during the rendering cycle
   - The page's markup file does NOT contain an explicit tag for the container, but does contain tags for its children

2. **Specifically verify the rendering path**:
   - Create a test page that extends `WebPage` and uses `NoopOutputTransformerContainer` (or similar) as a container
   - Add a child component (e.g., `SimpleBorder` with id `myBorder`) inside the container
   - Call `tester.startPage(testPage)` and assert that rendering succeeds without any `MarkupNotFoundException` or "Unable to find associated markup file" error
   - Verify the rendered output contains the child component's content

3. **Check the resource loading chain**:
   - The bug occurs when `getAssociatedMarkupResource()` (in `MarkupContainer`) is called on the transformer container itself
   - The fix ensures the stream is properly handled/closed in the `BufferedWebResponse` even when the container has no associated markup
   - Test that the page renders correctly when the container has NO corresponding markup file and relies entirely on child components

### Common pitfalls to avoid:
- ❌ **Testing only that rendering succeeds** without checking that child component content actually appears in the output
- ❌ **Assuming AbstractOutputTransformerContainer has its own markup file** — it shouldn't; it delegates rendering
- ❌ **Using a markup file for the container** — the test should verify the case where the container has NO dedicated markup
- ❌ **Not including child components** — the bug manifests when children are rendered through the transformer container
- ❌ **Testing with only simple components** — use a component like `Border` that has its own markup resource requirements

### Correct test approach:
```java
// Test page: Page_3.java
public class Page_3 extends WebPage {
    public Page_3() {
        NoopOutputTransformerContainer container = 
            new NoopOutputTransformerContainer("myContainer");
        add(container);
        container.add(new SimpleBorder("myBorder"));
    }
}
```
```java
// Page_3 markup (Page_3.html) — does NOT contain <div wicket:id="myContainer"> or any tag for the container
// But DOES contain <span wicket:id="myBorder"> for the border child
```

### Wrong test approach:
```java
// ❌ WRONG: Adding a markup file for the container itself defeats the purpose
// Page_3.html: <div wicket:id="myContainer"><span wicket:id="myBorder"/></div>

// ❌ WRONG: Not testing with real child components that need markup
public class Page_3 extends WebPage {
    public Page_3() {
        NoopOutputTransformerContainer container = 
            new NoopOutputTransformerContainer("containerOnly");
        add(container);
        // No children added — misses the bug
    }
}

// ❌ WRONG: Using a mock or stub instead of a real component lifecycle
```