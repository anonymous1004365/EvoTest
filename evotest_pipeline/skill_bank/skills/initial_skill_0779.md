---
name: advice-with-selection-targeting-precision
description: When using AdviceWith to weave .after() on child nodes inside a ChoiceDefinition,
  the TG must verify that the inserted node receives the correct messages and does
  not inadvertently apply to sibling branches. Use this skill to test that weaveByToString
  or weaveById targeting works correctly within conditional routing.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- ADVICE_WITH_ROUTE_INTERCEPTION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: INTERACTION_TEST
---

# advice-with-selection-targeting-precision

## Instructions

# AdviceWith Selection Targeting Precision

## Instructions

- WHEN the TG encounters a test that uses `adviceWith()` with `weaveByToString()` or `weaveById()` to insert mock endpoints (`.after().to("mock:...")`) into a route containing conditional branching (`choice()`/`when()`/`otherwise()`)
  - THEN the TG must verify that each inserted endpoint receives ONLY the messages that match its corresponding branch condition, NOT messages from sibling branches

- More specifically:
  - WHEN the route uses header-based predicates (e.g., `.when(header("foo"))`, `.when(header("bar"))`, `.otherwise()`) and the test sends messages with different headers that should trigger different branches
  - THEN the test must assert that each **inserted** endpoint (e.g., `mock:foo2`, `mock:bar2`) receives exactly the same message(s) and count as its **original** counterpart (e.g., `mock:foo`, `mock:bar`)

- Common pitfalls to avoid:
  - ❌ Testing only that the original endpoints get correct messages, while ignoring the **newly inserted** endpoints
  - ❌ Using `expectedMessageCount(1)` on an inserted endpoint when messages from other branches also incorrectly flow through it — the test must assert **specific body content** using `expectedBodiesReceived(...)` to prove no cross-branch leakage
  - ❌ Assuming that because `weaveByToString("To[mock:foo]").after().to("mock:foo2")` matches the correct node by `toString()`, the `.after()` insertion also maintains correct branch isolation — this is not guaranteed and must be verified explicitly
  - ❌ Sending messages that trigger only one branch and assuming all inserted endpoints behave correctly

- Correct approach (example):
  ```java
  // Route has: choice.when(header("foo")).to("mock:foo").id("foo")
  //             .when(header("bar")).to("mock:bar").id("bar")
  //             .otherwise().to("mock:baz").id("baz")
  
  route.adviceWith(context, new AdviceWithRouteBuilder() {
      @Override
      public void configure() throws Exception {
          weaveById("foo").after().to("mock:foo2");
          weaveById("bar").after().to("mock:bar2");
      }
  });

  // VERIFY: Each branch's inserted mock gets ONLY its own branch's message
  getMockEndpoint("mock:foo").expectedBodiesReceived("Hello World");
  getMockEndpoint("mock:foo2").expectedBodiesReceived("Hello World");   // only 1 message from "foo" branch
  getMockEndpoint("mock:bar").expectedBodiesReceived("Bye World");
  getMockEndpoint("mock:bar2").expectedBodiesReceived("Bye World");     // only 1 message from "bar" branch
  getMockEndpoint("mock:baz").expectedBodiesReceived("Hi World");

  template.sendBodyAndHeader("direct:start", "Hello World", "foo", "123");
  template.sendBodyAndHeader("direct:start", "Bye World", "bar", "123");
  template.sendBody("direct:start", "Hi World");

  assertMockEndpointsSatisfied();
  ```

- Incorrect approach (would miss the bug):
  ```java
  // BAD: Does not verify the inserted mock:foo2 and mock:bar2 endpoints at all
  getMockEndpoint("mock:foo").expectedMessageCount(1);
  getMockEndpoint("mock:bar").expectedMessageCount(1);
  getMockEndpoint("mock:baz").expectedMessageCount(1);
  // mock:foo2 would silently receive 2 messages (from both foo AND bar branches)
  ```