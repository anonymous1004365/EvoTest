---
name: jaxb-stream-unmarshal-close-reader
description: When unmarshalling XML with JAXB in streaming mode, the underlying reader/stream
  must be closed after unmarshalling to prevent resource leaks. This skill applies
  when using JaxbDataFormat with NonXmlFilterReader or any FilterReader wrapper around
  an InputStream.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
- STREAM_CLOSURE_AFTER_READ
test_pattern: INTERACTION_TEST
---

# jaxb-stream-unmarshal-close-reader

## Instructions

# JAXB Streaming Unmarshal Must Close the Reader

## Instructions

WHEN the TG encounters code that unmarshals JAXB data from an InputStream or Reader, especially when wrapping it in a `NonXmlFilterReader` or any `FilterReader` subclass, THEN the TG must verify that the underlying Java IO resource (`Reader`/`InputStream`) is properly closed after the unmarshalling operation completes.

WHEN using `JaxbDataFormat.unmarshal(Exchange, InputStream)` in a streaming or non-streaming context, THEN the TG should write a test that calls `unmarshal()` and then verifies that the wrapped `InputStream` or `Reader` has had its `close()` method called.

WHEN the `JaxbDataFormat` creates a `NonXmlFilterReader` wrapping the original stream in the `unmarshal()` method, THEN the TG must ensure the test exercises the full end-to-end flow: marshal an object to XML, then unmarshal the XML back, and check that no resource warnings or close failures occur. Specifically, verify that `javax.xml.stream.XMLStreamReader.close()` and `Reader.close()` are invoked after `createUnmarshaller().unmarshal()`.

WHEN verifying correct resource closure after JAXB unmarshalling, THEN the TG should NOT just check that no exceptions are thrown — it should also verify that the underlying stream/reader has its `close()` method called (e.g., by using a spy or by checking that closing the stream does not produce a warning). Common mistakes include:
- Assuming `FilterReader.close()` automatically propagates to the underlying wrapped reader (it does, but only if explicitly called on the wrapper)
- Testing only the unmarshal success without checking that the stream was closed after the operation
- Using a mock that ignores close without verification
- Testing only the happy path without verifying post-unmarshal resource state

Example of a correct test (spy-based verification):

```java
@Test
public void testUnmarshalClosesStream() throws Exception {
    JaxbDataFormat df = new JaxbDataFormat();
    df.setContextPath(MyBean.class.getPackage().getName());
    
    InputStream input = new ByteArrayInputStream("<myBean><name>Test</name></myBean>".getBytes());
    InputStream spyInput = Mockito.spy(input);
    
    Exchange exchange = new DefaultExchange(new DefaultCamelContext());
    Object result = df.unmarshal(exchange, spyInput);
    
    assertNotNull(result);
    assertTrue(result instanceof MyBean);
    
    // Verify the underlying stream was closed after unmarshal
    Mockito.verify(spyInput, Mockito.atLeastOnce()).close();
}
```

Example of an incorrect test (does not verify closure, would miss the bug):

```java
@Test
public void testUnmarshalOnlyChecksResult() throws Exception {
    JaxbDataFormat df = new JaxbDataFormat();
    df.setContextPath(MyBean.class.getPackage().getName());
    
    InputStream input = new ByteArrayInputStream("<myBean><name>Test</name></myBean>".getBytes());
    Exchange exchange = new DefaultExchange(new DefaultCamelContext());
    
    Object result = df.unmarshal(exchange, input);
    
    // BUG: This passes even if the stream is never closed,
    // allowing the resource leak to go undetected
    assertNotNull(result);
}
```