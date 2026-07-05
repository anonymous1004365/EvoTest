---
name: behavior-listener-enabled-check
description: When testing behavior request listeners (IRequestListener), verify that
  disabled behaviors throw ListenerInvocationNotAllowedException by testing with a
  behavior whose isEnabled(Component) returns false. The fix in ListenerRequestHandler.invoke()
  checks behavior.canCallListener(component) which calls isEnabled(component) && component.canCallListener().
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- CONVERSION_CHECK
- STATE_MUTATION
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: EXCEPTION_TEST
---

# behavior-listener-enabled-check

## Instructions

# Behavior Listener Enabled Check

## Instructions

- WHEN the TG encounters request handler code (e.g., `ListenerRequestHandler`) that invokes a behavior listener via `behavior.canCallListener(component)` or a similar check inside an `invoke()` method
- THEN the TG should write a test that:
  1. Creates a `Behavior` that implements `IRequestListener`
  2. Overrides `isEnabled(Component)` to return `false` for one behavior instance and `true` for another
  3. Adds both behaviors to a component
  4. Invokes the disabled behavior's listener (e.g., via `ListenerRequestHandler` constructed with the behavior's index)
  5. Verifies that calling the disabled behavior throws `ListenerInvocationNotAllowedException`
  6. Verifies that the disabled behavior's `onRequest()` was NOT called
  7. Also verifies that the enabled behavior's listener works normally (no exception, `onRequest()` was called)

- **The key insight**: the bug is that when a behavior implements `IRequestListener` and `isEnabled(Component)` returns `false`, invoking the listener on that behavior should throw `ListenerInvocationNotAllowedException`. Without this check, the listener is invoked even when the behavior reports itself as disabled.

- **Common pitfalls**:
  - Testing only component-level enabled/disabled state (via `Component.setEnabled(false)`) instead of behavior-level enabled/disabled state (via `Behavior.isEnabled(Component)`)
  - Testing only with enabled behaviors and not testing disabled behaviors
  - Not verifying that `onRequest()` was NOT called on the disabled behavior (the behavior should remain uncalled)
  - Forgetting to add behaviors to a component before creating `ListenerRequestHandler`

- **Incorrect example** (only tests component-level disabled, not behavior-level disabled):
  ```java
  // Incorrect: only tests component disabled, not behavior disabled
  component.setEnabled(false); // this disables the component, not the behavior
  ```

- **Correct example** (tests behavior-level enabled/disabled):
  ```java
  @Test
  public void disabledBehaviorRequest()
  {
      try
      {
          tester.executeUrl(urlForBehavior(page.disabledBehavior));
          fail("Executing the listener on disabled component is not allowed.");
      }
      catch (ListenerInvocationNotAllowedException expected)
      {
          assertFalse(page.disabledBehavior.wasCalled());
      }
  }
  
  private String urlForBehavior(Behavior behaviorUnderTest)
  {
      final int index = page.container.getBehaviorId(behaviorUnderTest);
      final IPageAndComponentProvider provider = new PageAndComponentProvider(page, page.container);
      final IRequestHandler handler = new ListenerRequestHandler(provider, index);
      return tester.urlFor(handler).toString();
  }
  ```
  
  Where the behavior overrides:
  ```java
  @Override
  public boolean isEnabled(Component component)
  {
      return component.isEnabledInHierarchy() && enabled;
  }
  ```