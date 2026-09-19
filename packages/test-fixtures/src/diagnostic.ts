type Modality = 'infrared' | 'acoustic' | 'partial_discharge';
type Severity = 'low' | 'medium' | 'high' | 'critical';

type DiagnosticEvent = {
  assetId: string;
  terminalId: string;
  edgeId: string;
  eventId: string;
  modality: Modality;
  capturedAt: string;
  defectType: string;
  confidence: number;
  severity: Severity;
  evidence: { uri: string; sha256: string };
};

type FileMetadata = {
  originalName: string;
  mediaType: string;
  sizeBytes: number;
  sha256: string;
};

const infraredEvent = {
  assetId: 'fixture-infrared-asset-001',
  terminalId: 'fixture-infrared-terminal-001',
  edgeId: 'fixture-infrared-edge-001',
  eventId: '018f0b7b-7b8a-7abc-8def-0123456789ab',
  modality: 'infrared',
  capturedAt: '2026-09-18T08:00:00.000Z',
  defectType: 'thermal-anomaly',
  confidence: 0.91,
  severity: 'high',
  evidence: {
    uri: 's3://fixture-evidence/infrared/sample-infrared.bin',
    sha256: 'a'.repeat(64),
  },
} as const satisfies DiagnosticEvent;

const acousticEvent = {
  assetId: 'fixture-acoustic-asset-001',
  terminalId: 'fixture-acoustic-terminal-001',
  edgeId: 'fixture-acoustic-edge-001',
  eventId: '018f0b7b-7b8b-7abc-8def-0123456789ab',
  modality: 'acoustic',
  capturedAt: '2026-09-18T08:00:20.000Z',
  defectType: 'abnormal-acoustic-pattern',
  confidence: 0.84,
  severity: 'medium',
  evidence: {
    uri: 's3://fixture-evidence/acoustic/sample-voiceprint.bin',
    sha256: 'b'.repeat(64),
  },
} as const satisfies DiagnosticEvent;

const partialDischargeEvent = {
  assetId: 'fixture-partial-discharge-asset-001',
  terminalId: 'fixture-partial-discharge-terminal-001',
  edgeId: 'fixture-partial-discharge-edge-001',
  eventId: '018f0b7b-7b8c-7abc-8def-0123456789ab',
  modality: 'partial_discharge',
  capturedAt: '2026-09-18T08:01:00.000Z',
  defectType: 'discharge-pulse-anomaly',
  confidence: 0.88,
  severity: 'critical',
  evidence: {
    uri: 's3://fixture-evidence/partial-discharge/sample-pd.bin',
    sha256: 'c'.repeat(64),
  },
} as const satisfies DiagnosticEvent;

export const validDiagnosticEvents = {
  infrared: infraredEvent,
  acoustic: acousticEvent,
  partialDischarge: partialDischargeEvent,
} as const satisfies Record<string, DiagnosticEvent>;

export const invalidDiagnosticFixtures = {
  missingId: {
    ...infraredEvent,
    assetId: undefined,
  },
  invalidModality: {
    ...infraredEvent,
    eventId: '018f0b7b-7b8d-7abc-8def-0123456789ab',
    modality: 'ultrasonic_video',
  },
  invalidTime: {
    ...infraredEvent,
    eventId: '018f0b7b-7b8e-7abc-8def-0123456789ab',
    capturedAt: '2026-02-30T25:61:61Z',
  },
} as const satisfies Record<string, Record<string, unknown>>;

export const boundaryDiagnosticFixtures = {
  confidenceMinimum: {
    ...infraredEvent,
    eventId: '018f0b7b-7b8f-7abc-8def-0123456789ab',
    confidence: 0,
  },
  confidenceMaximum: {
    ...infraredEvent,
    eventId: '018f0b7b-7b90-7abc-8def-0123456789ab',
    confidence: 1,
  },
  minimumFile: {
    originalName: 'minimum.bin',
    mediaType: 'application/octet-stream',
    sizeBytes: 1,
    sha256: 'd'.repeat(64),
  },
} as const satisfies {
  confidenceMinimum: DiagnosticEvent;
  confidenceMaximum: DiagnosticEvent;
  minimumFile: FileMetadata;
};

export const duplicateDiagnosticEvents = {
  first: { ...infraredEvent },
  replay: { ...infraredEvent },
} as const satisfies { first: DiagnosticEvent; replay: DiagnosticEvent };

export const safeFileMetadata = {
  originalName: 'sample-infrared.bin',
  mediaType: 'application/octet-stream',
  sizeBytes: 2048,
  sha256: 'a'.repeat(64),
} as const satisfies FileMetadata;
