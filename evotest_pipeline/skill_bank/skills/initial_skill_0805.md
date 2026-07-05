---
name: expression-evaluation-exception-preservation
description: When testing expressions that throw during evaluation in splitter/bean
  contexts, the test must verify the original cause exception is preserved and not
  wrapped in an unrelated exception type. This skill helps write tests that catch
  regression where ExpressionEvaluationException loses its cause chain.
code_tags:
- EXCEPTION_HANDLING
- NULL_CHECK
- EXPRESSION_EVALUATION_EXCEPTION_WRAPPING
test_pattern: EXCEPTION_TEST
---

# expression-evaluation-exception-preservation

## Instructions

# Expression Evaluation Exception Cause Preservation

## Instructions

WHEN the TG encounters code that wraps exceptions from expression evaluation (e.g., `ExpressionEvaluationException`, `OGNL`, `JXPath`, `JSONPath` expressions) and propagates them through a splitter or bean method invocation,

THEN the TG should write a test that:

1. **Creates an expression that throws a specific cause exception** (e.g., `IllegalArgumentException` with a distinct message) during evaluation.

2. **Passes that expression to a splitter** (`.split().method(...)` or `.split().expression(...)`) with a message that contains multiple items.

3. **Verifies the exception type and cause chain** using `assertThat` on the caught `Exception`:
   - The outer exception should be `CamelExecutionException`
   - The cause should contain the original exception type, not a generic `ExpressionEvaluationException` that silently loses the cause
   - Specifically check that the thrown exception's cause chain includes the original exception as a *direct or indirect* cause (use `getCause()`, `assertIsInstanceOf`, etc.)

4. **Mocks the Exchange with `MockEndpoint`** to assert that the splitter attempted at least some exchanges before failing — this confirms the split happened before the expression crash.

Common pitfalls to avoid:

- ❌ **Testing only that an exception is thrown**, without verifying the exception type and cause chain. A buggy version might throw a generic `RuntimeException` or `ExpressionEvaluationException` without preserving the originating cause.
- ❌ **Using `.split().body()` or simple split expressions** that don't invoke the expression evaluation path that triggers the bug. The splitter must use `.method(...)` or a custom expression that calls `evaluate()` on a `BeanExpression` or `Expression` implementation.
- ❌ **Forgetting to set up the splitter strategy** (e.g., `AggregationStrategy`) that is required for splitter error handling to work correctly in the test route.

### Example (Correct Test Pattern)

```java
public class SplitterExpressionExceptionTest extends ContextTestSupport {
    @Test
    public void testSplitterThrowExceptionVerifyCause() {
        MockEndpoint mock = getMockEndpoint("mock:split");
        mock.expectedMinimumMessageCount(1);
        
        try {
            template.sendBody("direct:start", "A,B,C");
            fail("Should have thrown exception");
        } catch (CamelExecutionException e) {
            // Verify the cause chain preserves the original exception from expression evaluation
            Throwable cause = e.getCause();
            assertIsInstanceOf(ExpressionEvaluationException.class, cause);
            // The expression evaluation exception itself should have a cause
            assertNotNull("ExpressionEvaluationException should wrap the original exception", cause.getCause());
            // The root cause should be the specific exception thrown by the expression
            assertIsInstanceOf(IllegalArgumentException.class, cause.getCause());
        }
    }
    
    @Override
    protected RouteBuilder createRouteBuilder() {
        return new RouteBuilder() {
            public void configure() {
                from("direct:start")
                    .split().method(MySplitBean.class, "splitExpression")
                    .to("mock:split");
            }
        };
    }
}
```

### Example (Incorrect Test Pattern — Missing Cause Verification)

```java
// BAD: Only checks an exception is thrown, never verifies the cause
@Test
public void testSplitterThrowException() {
    try {
        template.sendBody("direct:start", "A,B,C");
        fail("Should have thrown exception");
    } catch (Exception e) {
        // This test passes even if the exception is utterly wrong
        assertTrue(true);
    }
}
```