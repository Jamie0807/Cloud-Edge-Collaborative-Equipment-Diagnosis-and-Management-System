package com.diagnostics.cloudapi;

import java.time.Instant;

/** 云端保存的完整诊断事件。 */
public record DiagnosticEvent(
    String assetId,
    String terminalId,
    String edgeId,
    String eventId,
    String modality,
    String defectType,
    double confidence,
    String severity,
    Instant occurredAt,
    String evidenceUri) {}
