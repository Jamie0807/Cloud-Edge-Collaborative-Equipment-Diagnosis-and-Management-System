package com.diagnostics.cloudapi;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CloudApiApplicationTest {
  @Autowired private TestRestTemplate restTemplate;

  @LocalServerPort private int port;

  @Test
  void healthEndpointReturnsUp() {
    ResponseEntity<Map> response = restTemplate.getForEntity("/actuator/health", Map.class);

    assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
    assertThat(response.getBody()).containsEntry("status", "UP");
    assertThat(port).isPositive();
  }
}
