---
name: inputstream-body-ognl-consumption
description: When OGNL (or other expression languages) evaluates an expression against
  an InputStream body, the stream gets consumed and subsequent reads return 0 bytes.
  Tests must verify that bean methods using OGNL expressions receive the full, unconsumed
  body content.
code_tags:
- INPUTSTREAM_BODY_CONSUMPTION
test_pattern: INTERACTION_TEST
---

# inputstream-body-ognl-consumption

## Instructions

# InputStream Body Consumption in OGNL Expression Evaluation

## Instructions

- WHEN the TG encounters code that uses an OGNL expression (or similar expression language) to pass the message body to a bean method — e.g., `.bean(MyBean.class, "doSomething(${body})")` or `OgnlExpression.evaluate(exchange, body)` — AND the message body is an `InputStream` type
- THEN the TG must write a test that:
  1. Sets up a route using the relevant expression language (e.g., OGNL) in a bean method invocation with the body as a parameter
  2. Sends a message with an `InputStream` body containing known content (e.g., `new ByteArrayInputStream("some test data".getBytes())`) 
  3. Verifies that the bean method receives the **full, unconsumed content** — e.g., by calling `exchange.getIn().getBody(byte[].class)` or reading the InputStream inside the bean and comparing the content to the expected input
  4. Expects the test to **fail on the buggy version** because the body returns 0 bytes / empty content
- Common pitfalls to avoid:
  - **Testing only with String body types** — the bug only manifests with `InputStream` body types, so tests that use String bodies will pass on both buggy and fixed versions
  - **Using `getBody(String.class)` in assertions** — converting to String may also consume the stream; use `byte[]` or read the stream directly in the bean method
  - **Not including an explicit route definition** — the expression language evaluation is triggered during message routing, so the test must exercise the full route lifecycle
  - **Checking only the response/out message** — verify the bean method was actually called with the correct body content, not just that the exchange completed

### Correct test pattern (triggers the bug)

```java
// Correct: Tests OGNL expression with InputStream body — WILL FAIL on buggy version
@Test
public void testToBeanWithInputStreamBodyMethodOGNL() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").bean(MyBean.class, "doSomething(${body})");
        }
    });

    String expectedBody = "There is 11 bytes";
    template.sendBody("direct:start", new ByteArrayInputStream(expectedBody.getBytes()));

    // On buggy version: the bean receives an empty/0-byte body because OGNL
    // evaluation consumed the InputStream before the bean method was invoked
    // Expected: body contains "There is 11 bytes"
    // Actual: body is empty (0 bytes)
}
```

### Incorrect test pattern (does NOT trigger the bug)

```java
// WRONG: Uses String body — bug does NOT manifest with String types
@Test
public void testToBeanWithBodyMethodOGNL() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").bean(MyBean.class, "doSomething(${body})");
        }
    });

    // Sending a String body — this works fine on both buggy and fixed versions!
    template.sendBody("direct:start", "There is 11 bytes");
    
    // This test passes on both versions, giving false confidence
}
```