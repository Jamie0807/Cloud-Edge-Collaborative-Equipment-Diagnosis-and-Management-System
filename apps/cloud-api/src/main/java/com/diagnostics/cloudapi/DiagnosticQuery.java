package com.diagnostics.cloudapi;

import java.time.Instant;

/** 诊断查询条件，时间范围采用 UTC 左闭右开。 */
public record DiagnosticQuery(
    String assetId,
    String terminalId,
    String edgeId,
    String modality,
    Instant from,
    Instant to) {}
