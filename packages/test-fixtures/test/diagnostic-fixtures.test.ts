import {
  boundaryDiagnosticFixtures,
  duplicateDiagnosticEvents,
  invalidDiagnosticFixtures,
  safeFileMetadata,
  validDiagnosticEvents,
} from '../src/diagnostic';
import { validDiagnosticEvents as publicValidDiagnosticEvents } from '@diagnostics/test-fixtures';
import { describe, expect, it } from 'vitest';

const idNames = ['assetId', 'terminalId', 'edgeId', 'eventId'] as const;
const uuidV7Pattern = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const utcTimestampPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$/;

describe('诊断夹具', () => {
  it('通过包名入口导出相同的共享夹具', () => {
    expect(publicValidDiagnosticEvents).toBe(validDiagnosticEvents);
  });

  it('提供确定性的红外、声纹和局放事件', () => {
    expect(Object.keys(validDiagnosticEvents)).toEqual([
      'infrared',
      'acoustic',
      'partialDischarge',
    ]);

    for (const event of Object.values(validDiagnosticEvents)) {
      expect(event.modality).toMatch(/^(infrared|acoustic|partial_discharge)$/);
      expect(event.capturedAt).toMatch(utcTimestampPattern);
      expect(event.eventId).toMatch(uuidV7Pattern);
      expect(event.evidence.uri).toMatch(/^s3:\/\/[^\s/]+\/[^\s]+$/);
      for (const idName of idNames) {
        if (idName === 'eventId') expect(event[idName]).toMatch(uuidV7Pattern);
        else expect(event[idName]).toMatch(/^fixture-[a-z0-9-]+$/);
      }
      expect(event.confidence).toBeGreaterThanOrEqual(0);
      expect(event.confidence).toBeLessThanOrEqual(1);
      expect(['low', 'medium', 'high', 'critical']).toContain(event.severity);
    }
  });

  it('保持每个有效事件的四个标识语义独立', () => {
    for (const event of Object.values(validDiagnosticEvents)) {
      expect(new Set(idNames.map((idName) => event[idName])).size).toBe(4);
    }
  });

  it('提供缺少标识、非法模态和非法时间夹具', () => {
    expect(invalidDiagnosticFixtures.missingId).toMatchObject({
      assetId: undefined,
      terminalId: expect.any(String),
      edgeId: expect.any(String),
      eventId: expect.any(String),
    });
    expect(invalidDiagnosticFixtures.invalidModality.modality).toBe('ultrasonic_video');
    expect(invalidDiagnosticFixtures.invalidTime.capturedAt).toBe('2026-02-30T25:61:61Z');
  });

  it('提供置信度和最小文件大小边界夹具', () => {
    expect(boundaryDiagnosticFixtures.confidenceMinimum.confidence).toBe(0);
    expect(boundaryDiagnosticFixtures.confidenceMaximum.confidence).toBe(1);
    expect(boundaryDiagnosticFixtures.minimumFile.sizeBytes).toBe(1);
  });

  it('提供 eventId 相同且载荷一致的重复事件对', () => {
    expect(duplicateDiagnosticEvents.first.eventId).toBe(duplicateDiagnosticEvents.replay.eventId);
    expect(duplicateDiagnosticEvents.first).toEqual(duplicateDiagnosticEvents.replay);
  });

  it('提供不包含路径、凭据和文件正文的安全文件元数据', () => {
    expect(safeFileMetadata).toEqual({
      originalName: 'sample-infrared.bin',
      mediaType: 'application/octet-stream',
      sizeBytes: 2048,
      sha256: 'a'.repeat(64),
    });
    expect(JSON.stringify(safeFileMetadata)).not.toMatch(/password|token|secret|\/tmp|\\/);
  });
});
