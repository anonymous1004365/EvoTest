---
name: component-renderer-markup-null-check
description: When a component that overrides getMarkup() returns null, ComponentRenderer.renderComponent()
  should handle this gracefully instead of throwing a NullPointerException. Tests
  should verify that components returning null markup are handled without NPE.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# component-renderer-markup-null-check

## Instructions

# Component Renderer Null Markup Handling

## Instructions

- WHEN testing ComponentRenderer.renderComponent() with a component that overrides `getMarkup()` to return `null`
- THEN the test should verify that the renderer handles the null markup gracefully, rather than throwing a NullPointerException. The test should call `ComponentRenderer.renderComponent(component)` and assert that a meaningful exception with information about the component is thrown (e.g., an exception that includes the component ID or "Exception in rendering component" message), not a generic NullPointerException.
- Include concrete examples: create a test component class that extends, e.g., Panel or WebMarkupContainer, override `public IMarkupFragment getMarkup() { return null; }`, add it to a test page, and render it.
- Common pitfalls: testing only with components that have valid markup; assuming ComponentRenderer handles null markup without throwing; not testing the specific failure mode where getMarkup() returns null directly.

## Examples

Correct test approach:
```java
// Component that returns null markup
public class NullMarkupPanel extends Panel {
    public NullMarkupPanel(String id) {
        super(id);
    }
    @Override
    public IMarkupFragment getMarkup() {
        return null;
    }
}

@Test
public void renderComponentWithNullMarkup_DoesNotCauseNPE() {
    NullMarkupPanel panel = new NullMarkupPanel("compId");
    try {
        ComponentRenderer.renderComponent(panel);
        fail("Expected an exception but none was thrown");
    } catch (Exception e) {
        // Should be a meaningful exception, not NullPointerException
        assertThat(e).isNotInstanceOf(NullPointerException.class);
        assertThat(e.getMessage()).contains("compId");
    }
}
```

Incorrect test approach (what to avoid):
```java
// Only testing with components that always return valid markup
@Test
public void renderComponent() {
    Panel panel = new Panel("compId") {
        @Override
        public IMarkupFragment getMarkup() {
            return new MarkupFragment(...); // Always valid
        }
    };
    String result = ComponentRenderer.renderComponent(panel);
    // This passes but misses the null markup case entirely
}
```