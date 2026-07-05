---
name: output-transformer-container-behavior-mutation
description: Test that AbstractOutputTransformerContainer and AbstractTransformerBehavior
  correctly handle component mutations (like adding behaviors or changing tags) when
  child components transform output. Use when a component with a transformer behavior
  or container has children that themselves are transformed.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# output-transformer-container-behavior-mutation

## Instructions

# Output Transformer Container/Behavior Component Mutation Test Skill

## Instructions

WHEN a test exercises an `AbstractOutputTransformerContainer` or a component with an `AbstractTransformerBehavior` (such as `XsltTransformerBehavior`) where the component (or its children) have mutations applied (e.g., `AttributeModifier`, `setRenderBodyOnly`, nested transformer containers, or panels set to render body only), THEN the test must verify that the transformation logic still correctly handles all the mutated output, not just the basic unmodified markup.

Specifically:

- WHEN an `AbstractOutputTransformerContainer` with `transformBodyOnly=true` (the default) has child components that are themselves mutated (e.g., `Panel.setRenderBodyOnly(true)`, `Border`, `AttributeModifier`), THEN verify the full rendered HTML output matches the expected result including:
  - The transformed output from the container's `transform()` method
  - Nested component tag structures (e.g., wicket:body, wicket:border, wicket:panel markers)
  - Attribute modifications (e.g., `testAttr="myValue"`)  
  - Namespace declarations added by transformers (e.g., `xmlns:wicket`)
  - Case transformations or content replacements applied by the `transform()` method

- WHEN a component has both an `AbstractTransformerBehavior` (e.g., `XsltTransformerBehavior`) and an `AttributeModifier` applied, THEN verify that the behavior's `onComponentTag()` method (which adds `xmlns:wicket`) correctly interacts with the attribute modifier, and the final output preserves both.

- WHEN using `executeTest(PageClass.class, "ExpectedResultFile.html")` from `WicketTestCase`, THEN the expected result file must exactly match the rendered output, including all wicket namespace attributes, transformed case, and body-only rendering changes.

- Common pitfalls:
  - Testing only the basic transformation (e.g., changing a string) without verifying that component mutations (panels set to body-only, border elements, attribute modifiers) survive the transformation
  - Forgetting that `NoopOutputTransformerContainer` preserves child markup unchanged but still needs to render children through its infrastructure
  - Assuming that `setRenderBodyOnly(true)` on a panel nested inside a transformer container works the same as outside — verify the actual HTML output

**Correct example:**

```java
@Test
public void renderHomePage_2() throws Exception
{
    executeTest(Page_2.class, "PageExpectedResult_2.html");
}
```

Where `Page_2` creates:
- A `NoopOutputTransformerContainer("test")` containing a Label — output should include the container's body with the label
- An `AbstractOutputTransformerContainer("test2")` with `transform()` returning "Whatever" that contains a `Panel_1` with `setRenderBodyOnly(true)` — output should be exactly "Whatever" regardless of panel content
- An `AbstractOutputTransformerContainer("test3")` with `transform()` uppercasing output, containing a `SimpleBorder("myBorder")` — output must have the border's wicket:body/wicket:border tags in UPPERCASE
- A `SimpleBorder("myBorder2")` with `AttributeModifier.replace("testAttr", "myValue")` and an `XsltTransformerBehavior` — output must include both the attribute modifier's `testAttr="myValue"` and the xmlns:wicket namespace

**Incorrect example:**

```java
// Wrong: Only tests a simple transformer with no child mutations
@Test
public void renderSimpleTransformation() throws Exception
{
    // This would miss the bug where transformed containers with 
    // body-only panels, borders, or attribute modifiers produce wrong output
    executeTest(SimpleTransformationPage.class, "SimpleExpectedResult.html");
}
```