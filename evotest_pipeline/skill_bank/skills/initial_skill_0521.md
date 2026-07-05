---
name: try-catch-finally-setfault-body-preservation
description: When testing try-catch-finally blocks with setFaultBody, verify that
  the fault body set inside the try block is preserved after finally execution, rather
  than being replaced by the normal body. Use this skill whenever there's a try/finally
  processor with setFaultBody.
code_tags:
- STATE_MUTATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# try-catch-finally-setfault-body-preservation

## Instructions

# Try-Catch-Finally with setFaultBody State Preservation

## Instructions

- WHEN the TG encounters a route that uses `doTry().setFaultBody(...).doFinally()` pattern, where the `doFinally` block executes after a fault has been set via `setFaultBody`
- THEN the TG should write a test that verifies the fault body is preserved **after** the finally block executes. Specifically:
  - Create an exchange with a normal body (e.g., `"Hello World"`)
  - Inside the `doTry` block, set the fault body using `setFaultBody(constant("This is a fault message"))`
  - The `doCatch` or `doFinally` block should execute (e.g., log something or set an additional header)
  - After the route completes, assert that `exchange.getOut().getBody(String.class)` returns the fault message (e.g., `"This is a fault message"`) and NOT the original normal body
  - Also assert `exchange.getOut().isFault()` returns `true`
- WHEN the TG writes such a test, it should use `context.createFluentProducerTemplate().to("direct:start").withBody("Hello World").request()`
- Common pitfalls:
  - **Testing only without finally**: The bug manifests specifically when a `doFinally` block is present after the `setFaultBody`. A test without `doFinally` may pass on both buggy and fixed versions.
  - **Asserting the wrong body**: The test must assert the body is the fault message, not the original input body. On the buggy version, the fault body gets overwritten by the normal body after finally executes.
  - **Forgetting to check `isFault()`**: The fault flag should remain `true` after processing. On the buggy version, the fault body content may be lost but the fault flag should still be checked.

- Example of a correct test:
```java
public void testSetFaultFinally() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);

    Exchange out = context.createFluentProducerTemplate()
        .to("direct:start")
        .withBody("Hello World")
        .request(Exchange.class);

    assertEquals("This is a fault message", out.getMessage().getBody(String.class));
    assertTrue("Should be fault", out.getMessage().isFault());

    mock.assertIsSatisfied();
}
```

- Example of an **incorrect** test that would pass on the buggy version too:
```java
public void testSetFaultNoFinally() throws Exception {
    Exchange out = context.createFluentProducerTemplate()
        .to("direct:start")
        .withBody("Hello World")
        .request(Exchange.class);

    assertEquals("This is a fault message", out.getMessage().getBody(String.class));
    assertTrue(out.getMessage().isFault());
}
// This test never exercises the finally block, so it wouldn't catch the bug
```

- The buggy behavior: when `doFinally` is present, the `FinallyProcessor` may process the exchange after the fault body has been set, causing the fault body to be overwritten by the normal body. The fix ensures the fault body (and fault flag) are preserved across finally execution.