import { CONTRACT_NAMES, contractSchemas, validateContract } from '../src/identifiers';
import { describe, expect, it } from 'vitest';

const ids = {
  assetId: 'asset-transformer-01',
  terminalId: 'terminal-infrared-01',
  edgeId: 'edge-substation-01',
  eventId: '018f0b7b-7b8a-7abc-8def-0123456789ab',
};

const diagnostic = {
  ...ids,
  modality: 'infrared',
  occurredAt: '2026-09-18T01:02:03.000Z',
  evidenceUri: 's3://diagnostics/edge-substation-01/events/event-01.jpg',
  evidenceSha256: 'a'.repeat(64),
  defectType: 'thermal-anomaly',
  confidence: 0.98,
  severity: 'high',
  analyzedAt: '2026-09-18T01:02:04.000Z',
  receivedAt: '2026-09-18T01:02:05.000Z',
  status: 'SUCCEEDED',
};

describe('传输无关的诊断契约', () => {
  it('导出全部版本化契约 schema', () => {
    expect(CONTRACT_NAMES).toEqual([
      'terminalHeartbeat',
      'detectionUploadMetadata',
      'edgeStatusReport',
      'diagnosticEvent',
      'diagnosticQuery',
      'diagnosticQueryResponse',
      'unifiedError',
      'idempotentEventResponse',
    ]);
    for (const name of CONTRACT_NAMES) {
      expect(contractSchemas[name]).toMatchObject({
        $schema: 'https://json-schema.org/draft/2020-12/schema',
        type: 'object',
        additionalProperties: false,
      });
    }
  });

  it('接受只包含适用标识的终端心跳', () => {
    const heartbeat = {
      terminalId: ids.terminalId,
      edgeId: ids.edgeId,
      modality: 'infrared',
      sentAt: '2026-09-18T01:02:03.000Z',
    };

    expect(validateContract('terminalHeartbeat', heartbeat)).toEqual({ valid: true });
    expect(heartbeat).not.toHaveProperty('assetId');
    expect(heartbeat).not.toHaveProperty('eventId');
    expect(
      validateContract('terminalHeartbeat', { ...heartbeat, sentAt: '2026-02-30T25:61:61Z' }).valid,
    ).toBe(false);
  });

  it('接受安全的检测上传元数据并拒绝不安全文件名', () => {
    const metadata = {
      ...ids,
      modality: 'acoustic',
      capturedAt: '2026-09-18T01:02:03Z',
      file: {
        fileName: 'event-01.wav',
        contentType: 'audio/wav',
        sizeBytes: 1,
        sha256: 'b'.repeat(64),
      },
    };

    expect(validateContract('detectionUploadMetadata', metadata)).toEqual({ valid: true });
    expect(
      validateContract('detectionUploadMetadata', {
        ...metadata,
        file: { ...metadata.file, fileName: '../secrets.txt' },
      }).valid,
    ).toBe(false);
  });

  it('拒绝检测上传中缺少任一独立标识', () => {
    for (const idName of ['assetId', 'terminalId', 'edgeId', 'eventId'] as const) {
      const metadata = {
        ...ids,
        modality: 'infrared',
        capturedAt: '2026-09-18T01:02:03Z',
        file: {
          fileName: 'event-01.bin',
          contentType: 'application/octet-stream',
          sizeBytes: 1,
          sha256: 'b'.repeat(64),
        },
      };
      delete metadata[idName];
      expect(validateContract('detectionUploadMetadata', metadata).valid).toBe(false);
    }
  });

  it('校验边端资源指标和明确的不可用状态', () => {
    const report = {
      edgeId: ids.edgeId,
      site: 'site-shanghai-01',
      reportedAt: '2026-09-18T01:02:03Z',
      resources: {
        cpu: { value: 0.42, sampledAt: '2026-09-18T01:02:02Z', status: 'available' },
        memory: { value: 0.61, sampledAt: '2026-09-18T01:02:02Z', status: 'available' },
        gpu: { value: null, sampledAt: '2026-09-18T01:02:02Z', status: 'unsupported' },
        npu: { value: null, sampledAt: '2026-09-18T01:02:02Z', status: 'unavailable' },
      },
    };

    expect(validateContract('edgeStatusReport', report)).toEqual({ valid: true });
    expect(validateContract('edgeStatusReport', { ...report, edgeId: undefined }).valid).toBe(
      false,
    );
    expect(
      validateContract('edgeStatusReport', { ...report, resources: { cpu: null } }).valid,
    ).toBe(false);
  });

  it('接受成功和失败两种诊断事件', () => {
    expect(validateContract('diagnosticEvent', diagnostic)).toEqual({ valid: true });
    expect(
      validateContract('diagnosticEvent', {
        ...diagnostic,
        status: 'FAILED',
        error: { code: 'INTERNAL_ERROR', message: '模拟算法失败' },
        evidenceUri: undefined,
        evidenceSha256: undefined,
        defectType: undefined,
        confidence: undefined,
        severity: undefined,
        analyzedAt: undefined,
      }),
    ).toEqual({ valid: true });
    expect(validateContract('diagnosticEvent', { ...diagnostic, confidence: 1.01 }).valid).toBe(
      false,
    );
    expect(
      validateContract('diagnosticEvent', {
        ...diagnostic,
        occurredAt: '2026-09-18T01:02:03+08:00',
      }).valid,
    ).toBe(false);
    expect(
      validateContract('diagnosticEvent', { ...diagnostic, evidence: { unexpected: true } }).valid,
    ).toBe(false);
  });

  it('拒绝带凭据或不安全协议的证据地址', () => {
    expect(validateContract('diagnosticEvent', diagnostic)).toEqual({ valid: true });
    expect(
      validateContract('diagnosticEvent', {
        ...diagnostic,
        evidenceUri: 'https://user:secret@example.com/evidence',
      }).valid,
    ).toBe(false);
    expect(
      validateContract('diagnosticEvent', {
        ...diagnostic,
        evidenceUri: 'http://example.com/evidence',
      }).valid,
    ).toBe(false);
    expect(
      validateContract('diagnosticEvent', { ...diagnostic, evidenceUri: 'file:///etc/passwd' })
        .valid,
    ).toBe(false);
  });

  it('按 AND 语义校验 UTC 查询参数和分页响应', () => {
    const query = {
      assetId: [ids.assetId],
      terminalId: [ids.terminalId],
      edgeId: [ids.edgeId],
      modality: ['partial_discharge'],
      from: '2026-09-17T00:00:00Z',
      to: '2026-09-18T00:00:00Z',
      page: 1,
      size: 20,
    };
    const response = { items: [], page: 1, size: 20, total: 0 };

    expect(validateContract('diagnosticQuery', query)).toEqual({ valid: true });
    expect(validateContract('diagnosticQueryResponse', response)).toEqual({ valid: true });
    expect(validateContract('diagnosticQuery', { ...query, size: 101 }).valid).toBe(false);
    expect(
      validateContract('diagnosticQuery', {
        ...query,
        from: '2026-09-18T00:00:00Z',
        to: '2026-09-17T00:00:00Z',
      }).valid,
    ).toBe(false);
  });

  it('对未知字段和非 UTC 时间返回校验失败', () => {
    expect(
      validateContract('terminalHeartbeat', {
        terminalId: ids.terminalId,
        edgeId: ids.edgeId,
        modality: 'infrared',
        sentAt: '2026-09-18T01:02:03Z',
        unexpected: true,
      }).valid,
    ).toBe(false);
    expect(
      validateContract('terminalHeartbeat', {
        terminalId: ids.terminalId,
        edgeId: ids.edgeId,
        modality: 'infrared',
        sentAt: '2026-09-18T01:02:03+00:00',
      }).valid,
    ).toBe(false);
    expect(validateContract('diagnosticQuery', null).valid).toBe(false);
  });

  it('区分幂等接受、重复接受和冲突响应', () => {
    const error = {
      code: 'VALIDATION_ERROR',
      message: 'eventId 必填',
      correlationId: 'request-01',
      details: [{ field: 'eventId', reason: 'required' }],
    };
    expect(validateContract('unifiedError', error)).toEqual({ valid: true });
    expect(validateContract('unifiedError', { ...error, code: 'NOT_A_CODE' }).valid).toBe(false);
    expect(
      validateContract('idempotentEventResponse', {
        eventId: ids.eventId,
        outcome: 'ACCEPTED',
        created: true,
      }),
    ).toEqual({ valid: true });
    expect(
      validateContract('idempotentEventResponse', {
        eventId: ids.eventId,
        outcome: 'DUPLICATE_ACCEPTED',
        created: false,
      }),
    ).toEqual({ valid: true });
    expect(
      validateContract('idempotentEventResponse', {
        eventId: ids.eventId,
        outcome: 'CONFLICT',
        created: false,
        error: { ...error, code: 'IDEMPOTENCY_CONFLICT' },
      }),
    ).toEqual({ valid: true });
    expect(
      validateContract('idempotentEventResponse', {
        eventId: ids.eventId,
        outcome: 'CONFLICT',
        created: true,
        error,
      }).valid,
    ).toBe(false);
    expect(
      validateContract('idempotentEventResponse', {
        eventId: ids.eventId,
        outcome: 'ACCEPTED',
        created: false,
      }).valid,
    ).toBe(false);
  });
});
