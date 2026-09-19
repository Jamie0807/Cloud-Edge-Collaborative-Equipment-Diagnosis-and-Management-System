package com.diagnostics.cloudapi;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** 云端状态和诊断接收、查询 API。 */
@RestController
@RequestMapping("/api/v1")
public class CloudDiagnosticController {
  private final CloudDiagnosticService service;

  public CloudDiagnosticController(CloudDiagnosticService service) {
    this.service = service;
  }

  @PostMapping("/edge-statuses")
  public EdgeStatus receiveEdgeStatus(@RequestBody EdgeStatus status) {
    return service.receiveEdgeStatus(status);
  }

  @PostMapping("/diagnostic-events")
  public ResponseEntity<Map<String, Object>> receiveDiagnostic(
      @RequestBody DiagnosticEvent event) {
    IngestResult result = service.ingestDiagnostic(event);
    HttpStatus status = result.kind() == IngestResult.Kind.CREATED ? HttpStatus.CREATED : HttpStatus.OK;
    return ResponseEntity.status(status)
        .body(Map.of("kind", result.kind().name(), "event", result.event()));
  }

  @GetMapping("/diagnostic-events")
  public List<DiagnosticEvent> query(
      @RequestParam(required = false) String assetId,
      @RequestParam(required = false) String terminalId,
      @RequestParam(required = false) String edgeId,
      @RequestParam(required = false) String modality,
      @RequestParam(required = false) Instant from,
      @RequestParam(required = false) Instant to) {
    return service.query(new DiagnosticQuery(assetId, terminalId, edgeId, modality, from, to));
  }

  @GetMapping("/diagnostic-events/{eventId}")
  public DiagnosticEvent get(@PathVariable String eventId) {
    return service
        .query(new DiagnosticQuery(null, null, null, null, null, null))
        .stream()
        .filter(event -> event.eventId().equals(eventId))
        .findFirst()
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "诊断事件不存在"));
  }
}
