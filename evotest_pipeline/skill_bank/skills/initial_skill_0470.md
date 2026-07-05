---
name: idempotent-consumer-exception-handling
description: When an IdempotentConsumer encounters a repository exception during the
  add operation, ensure the exchange is not incorrectly marked as consumed and the
  exception is properly propagated to the error handler instead of being silently
  handled or skipped.
code_tags:
- ARGUMENT_VALIDATION
- OVERFLOW
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# idempotent-consumer-exception-handling

## Instructions

# Idempotent Consumer Exception Handling

## Instructions

- **WHEN** testing an `IdempotentConsumer` that uses a repository implementing `IdempotentRepository.add()` which can throw an exception:
  - **THEN** verify that when `add()` throws an exception (e.g., a `RuntimeException`), the `IdempotentConsumer` does NOT call `repository.remove()` on the exchange's message ID, as the exchange was never successfully added.
  - **THEN** verify that the exception thrown by `repository.add()` is propagated and NOT silently caught/ignored.
  - **THEN** verify that the exchange is not marked as "consumed" in the idempotent repository when the add operation fails.

- **WHEN** the `IdempotentConsumer` uses an `IdempotentOnCompletion` strategy that conditionally removes or adds entries based on the exchange outcome:
  - **THEN** ensure that when an exception occurs during `add()`, the `onCompletion` handler does NOT attempt to remove the exchange ID from the repository (since it was never added).
  - **THEN** test that the exchange's unit of work still completes normally (exception propagation), without leaving the repository in an inconsistent state.

- **Common pitfalls to avoid:**
  - Testing only the happy path where `add()` succeeds and `remove()` is called on completion — this misses the bug where a failed `add()` leads to a spurious `remove()` call.
  - Testing exception handling by throwing from `remove()` but not from `add()` — both operations must be independently tested for exception resilience.
  - Assuming that because `remove()` is called in `onCompletion`, it is always safe — a failing `add()` means the ID was never stored, so `remove()` should NOT be called.

- **Correct approach (concrete example):**
```java
// Test that a repository exception in add() propagates and does NOT trigger remove()
@Test
public void testRepoException() throws Exception {
    final String messageId = "testMessage";
    
    // Create a mock repository that throws on add()
    IdempotentRepository repo = mock(IdempotentRepository.class);
    when(repo.add(messageId)).thenThrow(new RuntimeException("Cannot add"));
    
    // Create exchange with the message ID
    Exchange exchange = new DefaultExchange(context);
    exchange.getIn().setHeader(Exchange.MESSAGE_ID, messageId);
    
    // The processor should propagate the exception
    try {
        processor.process(exchange);
        fail("Expected exception to be thrown");
    } catch (Exception e) {
        // verify the cause is the repository exception
        assertTrue(e.getCause() instanceof RuntimeException);
        assertEquals("Cannot add", e.getCause().getMessage());
    }
    
    // Verify remove() was NEVER called (since add() failed)
    verify(repo, never()).remove(messageId);
}
```

- **Incorrect approach (would miss the bug):**
```java
// THIS WILL NOT CATCH THE BUG: only tests remove() exception
@Test
public void testRemoveException() throws Exception {
    // This only tests the remove path, not the add failure path
    IdempotentRepository repo = mock(IdempotentRepository.class);
    when(repo.add(messageId)).thenReturn(true); // add succeeds
    when(repo.remove(messageId)).thenThrow(new RuntimeException("Cannot remove"));
    
    // Process the exchange successfully
    processor.process(exchange);
    
    // This test passes even if the bug exists — it never checks
    // what happens when add() itself fails
}
```