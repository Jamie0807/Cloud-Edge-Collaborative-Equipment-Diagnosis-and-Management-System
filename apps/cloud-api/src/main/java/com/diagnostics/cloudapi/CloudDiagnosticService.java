package com.diagnostics.cloudapi;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;
import org.springframework.stereotype.Service;

/** 云端诊断领域服务；当前使用内存仓储，后续由 PostgreSQL 适配器替换。 */
@Service
public class CloudDiagnosticService {
  private static final Duration EDGE_OFFLINE_AFTER = Duration.ofSeconds(60);

  private final Clock clock;
  private final Map<String, EdgeStatus> edgeStatuses = new ConcurrentHashMap<>();
  private final Map<String, DiagnosticEvent> diagnosticEvents = new ConcurrentHashMap<>();

  public CloudDiagnosticService() {
    this(Clock.systemUTC());
  }

  CloudDiagnosticService(Clock clock) {
    this.clock = clock;
  }

  public EdgeStatus receiveEdgeStatus(EdgeStatus status) {
    EdgeStatus received =
        new EdgeStatus(status.edgeId(), status.site(), status.reportedAt(), Instant.now(clock));
    edgeStatuses.put(status.edgeId(), received);
    return received;
  }

  public boolean isEdgeOnline(String edgeId, Instant now) {
    EdgeStatus status = edgeStatuses.get(edgeId);
    return status != null && !now.isAfter(status.receivedAt().plus(EDGE_OFFLINE_AFTER));
  }

  public IngestResult ingestDiagnostic(DiagnosticEvent event) {
    validate(event);
    DiagnosticEvent existing = diagnosticEvents.putIfAbsent(event.eventId(), event);
    if (existing == null) {
      return new IngestResult(IngestResult.Kind.CREATED, event);
    }
    if (existing.equals(event)) {
      return new IngestResult(IngestResult.Kind.DUPLICATE, existing);
    }
    throw new IdempotencyConflictException(event.eventId());
  }

  public List<DiagnosticEvent> query(DiagnosticQuery query) {
    Stream<DiagnosticEvent> stream = diagnosticEvents.values().stream();
    if (query.assetId() != null) stream = stream.filter(event -> query.assetId().equals(event.assetId()));
    if (query.terminalId() != null)
      stream = stream.filter(event -> query.terminalId().equals(event.terminalId()));
    if (query.edgeId() != null) stream = stream.filter(event -> query.edgeId().equals(event.edgeId()));
    if (query.modality() != null)
      stream = stream.filter(event -> query.modality().equals(event.modality()));
    if (query.from() != null) stream = stream.filter(event -> !event.occurredAt().isBefore(query.from()));
    if (query.to() != null) stream = stream.filter(event -> event.occurredAt().isBefore(query.to()));
    return stream
        .sorted(
            Comparator.comparing(DiagnosticEvent::occurredAt)
                .reversed()
                .thenComparing(DiagnosticEvent::eventId))
        .toList();
  }

  private static void validate(DiagnosticEvent event) {
    if (List.of(event.assetId(), event.terminalId(), event.edgeId(), event.eventId()).stream()
        .anyMatch(value -> value == null || value.isBlank())) {
      throw new IllegalArgumentException("四个业务标识均不能为空");
    }
    if (event.occurredAt() == null || event.evidenceUri() == null) {
      throw new IllegalArgumentException("发生时间和证据地址不能为空");
    }
    if (event.confidence() < 0 || event.confidence() > 1) {
      throw new IllegalArgumentException("置信度必须位于 0 到 1 之间");
    }
  }
}
