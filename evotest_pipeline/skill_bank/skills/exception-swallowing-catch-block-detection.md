---
name: exception-swallowing-catch-block-detection
description: WHEN a method has a broad catch block (e.g., catch (Exception e)) that
  only prints the stack trace or logs the exception without re-throwing, THEN test
  that domain-specific exceptions are properly propagated to the caller and not silently
  consumed. Verify that the method throws the expected exception type when invalid
  input is provided.
code_tags:
- EXCEPTION_HANDLING
- EXCEPTION_PROPAGATION
- CATCH_BLOCK
- ERROR_HANDLING
test_pattern: EXCEPTION_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - PASS_BOTH
  - BUG_DETECTED
  transition_tags: []
  keywords:
  - catch
  - exception
  - swallow
  - printStackTrace
  - propagation
  - e.printStackTrace
---

WHEN the TG encounters a method with a catch block like 'catch (Exception e) { e.printStackTrace(); }' or 'catch (Exception e) { log.error(...); }' without re-throwing, THEN: 1) Identify what domain-specific exceptions (e.g., DBAppException, IllegalArgumentException) the method should throw for invalid inputs. 2) Generate tests that provide invalid inputs expected to trigger those exceptions. 3) Verify the exception propagates to the caller (assertThrows). 4) On the buggy version, the exception may be swallowed and the method may return normally or throw a different exception type. 5) Test both the exception type and the exception message content.