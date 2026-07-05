---
name: wizard-model-reset-initializes-steps
description: When testing WizardModel.reset(), verify that after reset, each step
  has its wizardModel reference set to the model, not null. The bug occurs because
  reset() nulls activeStep before calling step.init(this), and steps that read wizardModel
  during init may get null.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
- STATE_CHECK
test_pattern: STATE_TEST
---

# wizard-model-reset-initializes-steps

## Instructions

# WizardModel.reset() Must Initialize Step WizardModel References

## Instructions

- WHEN testing the `WizardModel.reset()` method on a `WizardModel` that has steps added via `add(IWizardStep)` or `add(IWizardStep, ICondition)`
- THEN the test must verify that **after `reset()` is called**, every step's `getWizardModel()` method returns the **same `WizardModel` instance** (the expected behavior), not `null`.
- The test should:
  1. Create a `WizardModel` instance.
  2. Add multiple `WizardStep` instances (e.g., 2 or 3) using `model.add(step)`.
  3. Call `model.reset()`.
  4. Iterate over the steps using `model.stepIterator()`.
  5. For each step, cast to `WizardStep` and call `step.getWizardModel()`.
  6. Assert that the returned value equals the original `WizardModel` instance (e.g., `assertEquals(model, step.getWizardModel())`).
- The bug causes `getActiveStep()` to return `null` after `reset()` because `activeStep` is temporarily set to `null` before `setActiveStep()` is called with the next visible step. If `step.init(this)` is called when `activeStep == null`, it may cause steps to store a null model reference.
- **Common pitfalls to avoid:**
  - Do NOT assume that simply calling `reset()` and then `getActiveStep()` is sufficient — the bug may cause a non-null active step but steps may still have null model references.
  - Do NOT test with only one step — the bug manifests more clearly with multiple steps where the iterator can expose inconsistent state.
  - Do NOT skip verifying all individual steps' model references — testing only `getActiveStep()` after `reset()` may pass even when individual steps have null model references.
  - Do NOT test `reset()` without first adding steps to the model — calling `reset()` on an empty model throws an `IllegalStateException`.

### Correct test pattern (Java/JUnit 4):

```java
@Test
public void testResetInitsSteps()
{
    WizardModel model = new WizardModel();
    model.add(new WizardStep());
    model.add(new WizardStep());
    model.add(new WizardStep());
    model.reset();

    Iterator<IWizardStep> iterator = model.stepIterator();
    assertNotNull(iterator);

    while (iterator.hasNext())
    {
        WizardStep step = (WizardStep) iterator.next();
        assertEquals(model, step.getWizardModel());
    }
}
```

### Incorrect test pattern (would miss the bug):

```java
@Test
public void testReset()
{
    WizardModel model = new WizardModel();
    model.add(new WizardStep());
    model.reset();
    
    // Only tests getActiveStep() — this may return non-null but steps
    // could still have null wizardModel references
    assertNotNull(model.getActiveStep());
}
```