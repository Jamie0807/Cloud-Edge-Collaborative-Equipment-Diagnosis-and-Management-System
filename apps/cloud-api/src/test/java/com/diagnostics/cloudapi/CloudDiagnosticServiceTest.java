package com.diagnostics.cloudapi;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import org.junit.jupiter.api.Test;

class CloudDiagnosticServiceTest {
  private static final Instant BASE_TIME = Instant.parse("2026-09-19T12:00:00Z");

  @Test
  void edgeIsOnlineAtSixtySecondsAndOfflineAfterSixtySeconds() {
    CloudDiagnosticService service = new CloudDiagnosticService(fixedClock(BASE_TIME));
    service.receiveEdgeStatus(new EdgeStatus("edge-1", "site-a", BASE_TIME.minusSeconds(10), BASE_TIME));

    assertThat(service.isEdgeOnline("edge-1", BASE_TIME.plusSeconds(59))).isTrue();
    assertThat(service.isEdgeOnline("edge-1", BASE_TIME.plusSeconds(60))).isTrue();
    assertThat(service.isEdgeOnline("edge-1", BASE_TIME.plusSeconds(61))).isFalse();
  }

  @Test
  void duplicateEventIsIdempotentAndConflictingPayloadIsRejected() {
    CloudDiagnosticService service = new CloudDiagnosticService(fixedClock(BASE_TIME));
    DiagnosticEvent event = event("event-1", "asset-1", "terminal-1", "edge-1");

    assertThat(service.ingestDiagnostic(event).kind()).isEqualTo(IngestResult.Kind.CREATED);
    assertThat(service.ingestDiagnostic(event).kind()).isEqualTo(IngestResult.Kind.DUPLICATE);

    DiagnosticEvent conflict = event("event-1", "asset-2", "terminal-1", "edge-1");
    assertThatThrownBy(() -> service.ingestDiagnostic(conflict))
        .isInstanceOf(IdempotencyConflictException.class);
  }

  @Test
  void queryCombinesFiltersAndReturnsEmptyCollectionWhenNoRecordMatches() {
    CloudDiagnosticService service = new CloudDiagnosticService(fixedClock(BASE_TIME));
    service.ingestDiagnostic(event("event-1", "asset-1", "terminal-1", "edge-1"));
    service.ingestDiagnostic(event("event-2", "asset-2", "terminal-1", "edge-1"));

    List<DiagnosticEvent> matched =
        service.query(new DiagnosticQuery("asset-1", "terminal-1", "edge-1", "infrared", null, null));
    List<DiagnosticEvent> empty =
        service.query(new DiagnosticQuery("asset-9", null, null, null, null, null));

    assertThat(matched).extracting(DiagnosticEvent::eventId).containsExactly("event-1");
    assertThat(empty).isEmpty();
  }

  @Test
  void queryUsesUtcHalfOpenTimeRange() {
    CloudDiagnosticService service = new CloudDiagnosticService(fixedClock(BASE_TIME));
    service.ingestDiagnostic(event("event-1", "asset-1", "terminal-1", "edge-1"));

    List<DiagnosticEvent> result =
        service.query(
            new DiagnosticQuery(
                null,
                null,
                null,
                null,
                BASE_TIME.minusSeconds(1),
                BASE_TIME));

    assertThat(result).isEmpty();
  }

  private static Clock fixedClock(Instant instant) {
    return Clock.fixed(instant, ZoneOffset.UTC);
  }

  private static DiagnosticEvent event(String eventId, String assetId, String terminalId, String edgeId) {
    return new DiagnosticEvent(
        assetId,
        terminalId,
        edgeId,
        eventId,
        "infrared",
        "thermal-anomaly",
        0.91,
        "medium",
        BASE_TIME,
        "s3://evidence/events/" + eventId + ".json");
  }
}
