---
name: http-status-code-retry-boundary-testing
description: WHEN testing a method that determines retryability based on HTTP status
  codes (e.g., isNonRetryableHTTPCode), verify that all expected retryable status
  codes (408, 429, 500-599) are correctly treated as retryable, and test boundary
  codes (499, 500, 599, 600) for correct classification.
code_tags:
- RETRY_LOGIC
- BOUNDARY_CHECK
- HTTP_STATUS_CODE
- NULL_CHECK
- CONDITIONAL_BRANCH
test_pattern: PARAMETRIC_TEST
evolution:
  active: true
  priority: 0
  evidence:
    added: 1
retrieval:
  applicable_tiers:
  - BUG_DETECTED
  - PASS_BOTH
  transition_tags: []
  keywords:
  - isNonRetryableHTTPCode
  - retry
  - HTTP status code
  - '429'
  - '408'
  - retryable
  - non-retryable
  - status code boundary
  - RestRequest
---

WHEN the focal method determines retryability based on HTTP status codes using a boolean condition chain with exclusions: 1) Identify each status code that should be retryable (408, 429, 500-599). 2) Test each exclusion individually with assertFalse(method(code)) for retryable codes. 3) Test boundary codes: 499 (just below 500, non-retryable), 500 (retryable), 599 (retryable), 600 (just above 599, non-retryable). 4) Test null response (should be retryable) and null status line (should throw NPE). 5) Test 403 behavior with both retryHTTP403=true and false flags.