---
name: socket-appender-reconnect-header-loss
description: When testing socket appender reconnect scenarios where the appender uses
  a managed connection with header configuration, verify that the header is properly
  re-sent during reconnection. The bug manifests as "No header" failure message during
  reconnection events.
code_tags:
- SOCKET_APPENDER_HEADER_CONFIG
- RESOURCE_MANAGEMENT
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# socket-appender-reconnect-header-loss

## Instructions

# Socket Appender Reconnect Header Loss

## Instructions

- WHEN the TG encounters a `SocketAppender` (or similar network appender) that connects to a remote server using a layout with a `Header` (e.g., `SerializedLayout`), and the appender is configured to reconnect on connection failure
- THEN the TG should write a test that:
  1. Starts a mock/bare-bones TCP server that accepts connections and captures the first bytes received (the header)
  2. Configures a `SocketAppender` pointing to this mock server (e.g., using `log4j-socket.xml` or programmatic configuration)
  3. Sends at least one log event to establish the initial connection
  4. Simulates a connection drop (close the server socket), then restarts the mock server to accept a new connection
  5. Sends another log event by logging via the appender
  6. Verifies that the header bytes are present at the beginning of the data received on the **second** (reconnected) connection

- The test should expect a failure like "No header" or "header missing" on the buggy version, and pass on the fixed version
- Common pitfalls:
  - Testing only the initial connection without simulating a reconnect/disconnect cycle
  - Using a unit test that only checks header presence on the first connection and assumes it carries over
  - Assuming that internal state (like the header bytes) persists correctly after the underlying socket/connection is replaced
  - Not waiting for the async appender to flush before asserting on received data

### Correct example

```java
// Start mock TCP server, capture header data from the first connection
MockTcpServer server = new MockTcpServer(port);
server.start();

// Create SocketAppender pointing to the mock server
SocketAppender appender = SocketAppender.newBuilder()
    .setName("test")
    .setConfiguration(config)
    .setLayout(SerializedLayout.createLayout())
    .setReconnectDelayMillis(100)
    .build();
appender.start();

// Log an event — this triggers the initial connection and sends header + event
logger.error("test message 1");

// Close the first server connection, simulating a network drop
server.closeClientSocket();
Thread.sleep(200); // wait for reconnect

// Start a NEW server instance on the same port to accept the reconnection
MockTcpServer server2 = new MockTcpServer(port);
server2.start();
Thread.sleep(500); // wait for appender to reconnect

// Log another event — this triggers reconnection and should re-send header
logger.error("test message 2");
Thread.sleep(500); // wait for async send

// Verify: the data received on the SECOND connection must start with the header
byte[] data = server2.getReceivedData();
assertNotNull("No header on reconnect", data);
// Header should be present at the beginning of the received data
String header = new String(data, StandardCharsets.UTF_8).substring(0, ...);
assertTrue("Header missing on reconnect", header.contains("expected-header-content"));
```

### Incorrect example (pitfall)

```java
// Only testing the initial connection — does NOT catch the reconnect bug
MockTcpServer server = new MockTcpServer(port);
server.start();

SocketAppender appender = SocketAppender.newBuilder()
    .setName("test")
    .setConfiguration(config)
    .setLayout(SerializedLayout.createLayout())
    .build();
appender.start();

logger.error("test message");
Thread.sleep(500);

byte[] data = server.getReceivedData();
assertNotNull("No header", data);
// This test passes even on the buggy version because the
// header IS sent on the first connection. It fails to detect
// that header is NOT re-sent after reconnection.
```