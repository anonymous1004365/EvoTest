---
name: file-idempotent-repository-state-test
description: WHEN a test configures a FileIdempotentRepository with a file store path,
  the test should verify that messages are correctly idempotent-processed (first message
  passes, duplicate is skipped). THEN write a test that sends two identical messages
  and asserts the first is processed while the second is not.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- FILE_IDEMPOTENT_REPOSITORY
- STATE_PERSISTENCE_FILE
- IDEMPOTENT_CONSUMER
test_pattern: INTERACTION_TEST
---

# file-idempotent-repository-state-test

## Instructions

# File Idempotent Repository State Persistence Test

## Instructions

WHEN the TG encounters code that uses a `FileIdempotentRepository` (configured via `FileIdempotentRepository.fileIdempotentRepository(new File("..."), ...)` in a Spring XML, Java DSL, or CDI `@Produces` context) as part of an idempotent consumer route:

- THEN the TG should write an integration or Spring-based test that sends at least two identical messages (same body/header content) through the route and verifies the idempotent behavior: the first message is processed (Body arrives at a mock endpoint unchanged), and the duplicate is skipped (no further deliveries).

- The test must use the same FileIdempotentRepository configuration (e.g., binary file store path, cache size, or file store size) as the code under test. Crucially, the test must verify the expected message body at the final mock endpoint — not just that headers or exchange properties changed.

- A common pitfall: Testing only that the route compiles and starts, or that an idempotent consumer configuration is present, without ever sending a duplicate message and asserting that the second copy is dropped. Another pitfall: Asserting on a mock endpoint but not clearing it between sends, causing the first and second messages to both appear. Always use separate `expectedMessageCount` and `assertIsSatisfied()` calls per attempt, or reset mocks between sends.

- The test should also verify that the repository **file** is created on disk (e.g., `assertTrue(file.exists())`) and that the file's content reflects the processed message key.

## Examples

### Correct Pattern (Catches the Bug)

```java
public class FileConsumerIdempotentTest extends CamelSpringTestSupport {
    @Override
    protected AbstractXmlApplicationContext createApplicationContext() {
        return new ClassPathXmlApplicationContext("org/apache/camel/spring/processor/idempotent/fileConsumerIdempotentTest.xml");
    }

    @Test
    public void testIdempotent() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        
        // First send — should be processed
        mock.expectedMessageCount(1);
        mock.expectedBodiesReceived("Hello World");
        template.sendBodyAndHeader("file://target/idempotent/", "Hello World", Exchange.FILE_NAME, "test.txt");
        assertMockEndpointsSatisfied();
        
        // Reset and send duplicate — should be skipped
        mock.reset();
        mock.expectedMessageCount(0);
        template.sendBodyAndHeader("file://target/idempotent/", "Hello World", Exchange.FILE_NAME, "test.txt");
        assertMockEndpointsSatisfied();
    }
}
```

### Incorrect Pattern (Misses the Bug)

```java
// ❌ Only tests that the route starts, never verifies idempotent behavior
public class FileConsumerIdempotentTest extends CamelSpringTestSupport {
    @Override
    protected AbstractXmlApplicationContext createApplicationContext() {
        return new ClassPathXmlApplicationContext("...");
    }

    @Test
    public void testRouteStarts() throws Exception {
        // No mock expectations, no message sending
        // This passes even if the idempotent filter drops ALL messages (including first)
    }
}
```

```java
// ❌ Tests idempotency by checking the mock count but only sends one message
public class FileConsumerIdempotentTest extends CamelSpringTestSupport {
    @Test
    public void testSingleMessage() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(1);
        template.sendBodyAndHeader("file://target/idempotent/", "Hello World", Exchange.FILE_NAME, "test.txt");
        assertMockEndpointsSatisfied();
        // Never sends a duplicate — never checks that the second is filtered
    }
}
```