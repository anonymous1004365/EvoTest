---
name: file-exist-ignore-does-not-write-body
description: When a file producer is configured with fileExist=Ignore and the target
  file already exists, the file must not be overwritten and the body must still contain
  the original message content. This skill teaches how to test that the Ignore option
  preserves the existing file without corrupting the exchange body.
code_tags:
- CONDITIONALLY_SKIP_FILE_WRITE
- STATE_MUTATION
test_pattern: STATE_TEST
---

# file-exist-ignore-does-not-write-body

## Instructions

# FileExist Ignore Must Preserve Existing File Content

## Instructions

WHEN the TG encounters a file producer endpoint with `fileExist=Ignore` and a target file that already exists on disk:

- THEN the TG should verify that after the route processes an exchange, the existing target file's content remains unchanged (i.e., it retains its original content before the route ran).
- THEN the TG should verify that the exchange body is **not** set to `null` after the route processes — the Ignore option must skip writing to the file but must NOT modify the exchange body.
- THEN the TG should set up the test scenario by:
  1. Creating a target file on disk with known content (e.g., `"Hello World"`) before sending the exchange.
  2. Sending a message through the route with `&amp;fileExist=Ignore` option.
  3. After the exchange completes, reading the target file's content back and asserting it equals the original content.
  4. Also extracting the exchange body from the mock endpoint and asserting it is NOT null and contains the expected original content.
- THEN the TG must expect that on the buggy version, the body becomes `null` after Ignore processing (failure message: `Body of message: 0. Expected: <Hello World> but was: <null>`), while on the fixed version the body retains its value.

Common pitfalls:
- **Pitfall: Only checking the file on disk.** The TG might verify the file is unchanged but forget to assert the exchange body is preserved. The bug manifests as a null body, so the test must check both the file content and the exchange body.
- **Pitfall: Using `Override` or other fileExist modes by mistake.** The test must use `Ignore` specifically — other modes behave differently and will not catch this bug.
- **Pitfall: Not ensuring the target file exists before the route runs.** If the file does not pre-exist, the Ignore option is not triggered, and the test will pass even on the buggy version.
- **Pitfall: Forgetting to give the poller enough time to process.** Use `mockEndpoint.assertIsSatisfied()` with a reasonable timeout (e.g., 2 seconds via `setResultWaitTime(2000)`) to ensure the file producer has completed processing.

**Correct example (Java with Camel test DSL):**
```java
public class FileProducerFileExistIgnoreTest extends ContextTestSupport {
    @Test
    public void testIgnore() throws Exception {
        // Pre-create the target file with known content
        template.sendBodyAndHeader("file://target/ignoretest", "Hello World", Exchange.FILE_NAME, "hello.txt");
        
        // Set up mock endpoint to capture the result
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedBodiesReceived("Hello World");
        mock.setResultWaitTime(2000);
        
        // Send a different body through the Ignore endpoint
        template.sendBodyAndHeader("file://target/ignoretest?fileExist=Ignore", "Bye World", Exchange.FILE_NAME, "hello.txt");
        
        // Let the file producer process
        mock.assertIsSatisfied();
        
        // Read the file back — it should still contain the original content
        String fileContent = context.getTypeConverter().convertTo(String.class, 
            new File("target/ignoretest/hello.txt"));
        assertEquals("File content should not be overwritten", "Hello World", fileContent);
        
        // The exchange body should also not be null
        assertNotNull("Body should not be null after Ignore", mock.getExchanges().get(0).getIn().getBody());
    }
}
```

**Incorrect example (what NOT to do):**
```java
// BAD: Only checks the file, does not verify the body
public void testIgnore() throws Exception {
    template.sendBodyAndHeader("file://target/ignoretest", "Hello World", Exchange.FILE_NAME, "hello.txt");
    template.sendBodyAndHeader("file://target/ignoretest?fileExist=Ignore", "Bye World", Exchange.FILE_NAME, "hello.txt");
    
    // This passes even on buggy version because file on disk is unchanged
    String fileContent = ...; // reads "Hello World"
    assertEquals("Hello World", fileContent);
    
    // MISSING: assertion on the exchange body — the bug is that body becomes null
}
```