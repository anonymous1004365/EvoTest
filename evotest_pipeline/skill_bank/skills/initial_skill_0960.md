---
name: throttler-jmx-race-condition
description: Teach the TG to detect race conditions in throttler implementations where
  the maximum requests per period can be updated asynchronously via JMX while exchanges
  are concurrently in flight, causing the throttler to allow too many or too few requests.
  Apply this skill when the code uses volatile fields for rate configuration with
  separate sync and async update paths.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# throttler-jmx-race-condition

## Instructions

# Throttler JMX Race Condition

## Instructions

- WHEN the TG encounters a `Throttler` implementation that has a `getCurrentMaximumRequestsPerPeriod()` method backed by a `volatile` field (e.g., `throttleRate`) and a separate async/sync update path (e.g., `setCurrentMaximumRequestsPerPeriod()` which updates the volatile field independently of the running sync block)
- THEN the TG should write a test that:
  1. Sends a batch of exchanges (e.g., 10 exchanges) at a controlled rate through a throttler configured with a specific maximum requests per period (e.g., 1 request per 100ms)
  2. While exchanges are in flight (within a separate thread or during the send), asynchronously calls the `setCurrentMaximumRequestsPerPeriod()` method (e.g., via JMX or direct setter) to **increase** the rate limit (e.g., from 1 to 10 requests per period)
  3. Verifies that the total number of exchanges processed does not exceed the **original** limit for the first time window — i.e., the throttler should still enforce the limit that was in effect when the exchanges were scheduled, not the updated limit
  4. The test should expect on the **buggy** version that more exchanges than allowed pass through (e.g., expecting 10 but getting 9 or 11), and on the **fixed** version that exactly the allowed count passes through (e.g., exactly 10)

- Common pitfalls to avoid:
  - **Testing only the sync path**: Do not just test that `getCurrentMaximumRequestsPerPeriod()` returns the correct value after `setCurrentMaximumRequestsPerPeriod()` is called — that misses the race condition entirely
  - **Not using a separate thread**: The race condition requires concurrent modification. Merely calling the setter before sending exchanges does not trigger the bug
  - **Assuming volatile provides atomicity**: A `volatile` field ensures visibility across threads but does NOT protect against read-modify-write races when a sync block also reads the same field
  - **Testing only decrease**: The bug is more easily triggered when the limit is **increased** mid-flight, allowing extra exchanges to leak through. Testing only a decrease may not trigger the race

- **Correct example** (triggers the bug):
  ```java
  @Test
  public void testConcurrentRateUpdateDuringThrottling() throws Exception {
      context.getRouteDefinitions().clear();
      context.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:start")
                  .throttle(1).timePeriodMillis(500)
                  .to("mock:result");
          }
      });
      context.start();

      MockEndpoint mock = getMockEndpoint("mock:result");
      mock.expectedMessageCount(10);

      // Send 10 messages in quick succession
      for (int i = 0; i < 10; i++) {
          template.sendBody("direct:start", "Message " + i);
      }

      // While exchanges are being throttled, increase the rate limit
      Throttler throttler = (Throttler) context.getProcessor("throttler");
      throttler.setCurrentMaximumRequestsPerPeriod(10);

      assertMockEndpointsSatisfied();
      // On buggy version: >10 messages may pass through
      // On fixed version: exactly 10 messages pass through
  }
  ```

- **Incorrect example** (misses the bug):
  ```java
  @Test
  public void testRateUpdate() throws Exception {
      // Only tests the getter/setter in isolation — no concurrency
      Throttler throttler = new Throttler(null, 5, 1000);
      assertEquals(5, throttler.getCurrentMaximumRequestsPerPeriod());
      throttler.setCurrentMaximumRequestsPerPeriod(10);
      assertEquals(10, throttler.getCurrentMaximumRequestsPerPeriod());
      // This test passes on both buggy and fixed versions!
  }
  ```