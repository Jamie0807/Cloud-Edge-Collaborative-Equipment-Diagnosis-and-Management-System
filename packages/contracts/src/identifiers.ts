type JsonSchema = {
  $schema?: string;
  type?: string | readonly string[];
  additionalProperties?: boolean;
  properties?: Readonly<Record<string, JsonSchema>>;
  required?: readonly string[];
  items?: JsonSchema;
  minLength?: number;
  pattern?: string;
  enum?: readonly unknown[];
  const?: unknown;
  minimum?: number;
  maximum?: number;
  minItems?: number;
  uniqueItems?: boolean;
  default?: unknown;
  description?: string;
  oneOf?: readonly JsonSchema[];
  not?: JsonSchema;
};

type ValidationError = { path: string; message: string };
type ValidationResult = { valid: true } | { valid: false; errors: ValidationError[] };

const schemaUrl = 'https://json-schema.org/draft/2020-12/schema';
const utcTimestampPattern = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?Z$/;

const id: JsonSchema = { type: 'string', minLength: 1 };
const eventId: JsonSchema = {
  type: 'string',
  pattern: '^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
};
const utcTimestamp: JsonSchema = {
  type: 'string',
  pattern: utcTimestampPattern.source,
  description: '带 Z 后缀的 ISO-8601 UTC 时间。',
};
const modality: JsonSchema = {
  type: 'string',
  enum: ['infrared', 'acoustic', 'partial_discharge'],
};
const severity: JsonSchema = { type: 'string', enum: ['low', 'medium', 'high', 'critical'] };
const evidenceSha256: JsonSchema = { type: 'string', pattern: '^[0-9a-fA-F]{64}$' };

const base = (
  properties: Readonly<Record<string, JsonSchema>>,
  required: readonly string[] = [],
): JsonSchema => ({
  $schema: schemaUrl,
  type: 'object',
  additionalProperties: false,
  properties,
  required,
});

const errorSchema: JsonSchema = base(
  {
    code: {
      type: 'string',
      enum: [
        'VALIDATION_ERROR',
        'NOT_FOUND',
        'DEPENDENCY_UNAVAILABLE',
        'UNAUTHORIZED',
        'FORBIDDEN',
        'IDEMPOTENCY_CONFLICT',
        'INTERNAL_ERROR',
      ],
    },
    message: { type: 'string', minLength: 1 },
    correlationId: id,
    details: {
      type: 'array',
      items: base(
        { field: { type: 'string', minLength: 1 }, reason: { type: 'string', minLength: 1 } },
        ['field', 'reason'],
      ),
    },
  },
  ['code', 'message'],
);

const metric: JsonSchema = base(
  {
    value: { type: ['number', 'null'], minimum: 0, maximum: 1 },
    sampledAt: utcTimestamp,
    status: { type: 'string', enum: ['available', 'unavailable', 'unsupported'] },
  },
  ['value', 'sampledAt', 'status'],
);

const diagnosticProperties: Readonly<Record<string, JsonSchema>> = {
  assetId: id,
  terminalId: id,
  edgeId: id,
  eventId,
  modality,
  occurredAt: utcTimestamp,
  evidenceUri: {
    type: 'string',
    pattern: '^(?:s3://[^\\s/@]+/[^\\s]+|https://[^\\s/@]+/[^\\s]+)$',
    description: '受控对象 URI 或短时授权 HTTPS 地址，不得包含凭据。',
  },
  evidenceSha256,
  defectType: { type: 'string', minLength: 1 },
  confidence: { type: 'number', minimum: 0, maximum: 1 },
  severity,
  analyzedAt: utcTimestamp,
  receivedAt: utcTimestamp,
  status: { type: 'string', enum: ['SUCCEEDED', 'FAILED'] },
  error: errorSchema,
};
const diagnosticRequired = [
  'assetId',
  'terminalId',
  'edgeId',
  'eventId',
  'modality',
  'occurredAt',
  'receivedAt',
  'status',
];

const diagnosticEventSchema: JsonSchema = {
  ...base(diagnosticProperties, diagnosticRequired),
  oneOf: [
    {
      properties: { status: { const: 'SUCCEEDED' } },
      required: [
        'evidenceUri',
        'evidenceSha256',
        'defectType',
        'confidence',
        'severity',
        'analyzedAt',
      ],
    },
    { properties: { status: { const: 'FAILED' } }, required: ['error'] },
  ],
};

const idempotencyConflictError: JsonSchema = {
  ...errorSchema,
  properties: {
    ...errorSchema.properties,
    code: { const: 'IDEMPOTENCY_CONFLICT' },
  },
};

const schemas = {
  terminalHeartbeat: base({ terminalId: id, edgeId: id, modality, sentAt: utcTimestamp }, [
    'terminalId',
    'edgeId',
    'modality',
    'sentAt',
  ]),
  detectionUploadMetadata: base(
    {
      assetId: id,
      terminalId: id,
      edgeId: id,
      eventId,
      modality,
      capturedAt: utcTimestamp,
      file: base(
        {
          fileName: { type: 'string', pattern: '^[^/\\\\]+$', minLength: 1 },
          contentType: {
            type: 'string',
            enum: [
              'image/jpeg',
              'image/png',
              'audio/wav',
              'audio/flac',
              'application/octet-stream',
            ],
          },
          sizeBytes: { type: 'integer', minimum: 1 },
          sha256: evidenceSha256,
        },
        ['fileName', 'contentType', 'sizeBytes', 'sha256'],
      ),
    },
    ['assetId', 'terminalId', 'edgeId', 'eventId', 'modality', 'capturedAt', 'file'],
  ),
  edgeStatusReport: base(
    {
      edgeId: id,
      site: { type: 'string', minLength: 1 },
      reportedAt: utcTimestamp,
      resources: base({ cpu: metric, memory: metric, gpu: metric, npu: metric }, [
        'cpu',
        'memory',
        'gpu',
        'npu',
      ]),
    },
    ['edgeId', 'site', 'reportedAt', 'resources'],
  ),
  diagnosticEvent: diagnosticEventSchema,
  diagnosticQuery: base({
    assetId: { type: 'array', items: id, minItems: 1, uniqueItems: true },
    terminalId: { type: 'array', items: id, minItems: 1, uniqueItems: true },
    edgeId: { type: 'array', items: id, minItems: 1, uniqueItems: true },
    modality: { type: 'array', items: modality, minItems: 1, uniqueItems: true },
    from: utcTimestamp,
    to: utcTimestamp,
    page: { type: 'integer', minimum: 1, default: 1 },
    size: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
  }),
  diagnosticQueryResponse: base(
    {
      items: { type: 'array', items: diagnosticEventSchema },
      page: { type: 'integer', minimum: 1 },
      size: { type: 'integer', minimum: 1, maximum: 100 },
      total: { type: 'integer', minimum: 0 },
    },
    ['items', 'page', 'size', 'total'],
  ),
  unifiedError: errorSchema,
  idempotentEventResponse: {
    ...base(
      {
        eventId,
        outcome: { type: 'string', enum: ['ACCEPTED', 'DUPLICATE_ACCEPTED', 'CONFLICT'] },
        created: { type: 'boolean' },
        error: errorSchema,
      },
      ['eventId', 'outcome', 'created'],
    ),
    oneOf: [
      {
        properties: { outcome: { const: 'ACCEPTED' }, created: { const: true } },
        not: { required: ['error'] },
      },
      {
        properties: { outcome: { const: 'DUPLICATE_ACCEPTED' }, created: { const: false } },
        not: { required: ['error'] },
      },
      {
        properties: {
          outcome: { const: 'CONFLICT' },
          created: { const: false },
          error: idempotencyConflictError,
        },
        required: ['error'],
      },
    ],
  },
} satisfies Record<string, JsonSchema>;

export const contractSchemas = schemas;
export const CONTRACT_NAMES = [
  'terminalHeartbeat',
  'detectionUploadMetadata',
  'edgeStatusReport',
  'diagnosticEvent',
  'diagnosticQuery',
  'diagnosticQueryResponse',
  'unifiedError',
  'idempotentEventResponse',
] as const satisfies readonly (keyof typeof schemas)[];

type ContractName = keyof typeof schemas;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);

const typeMatches = (value: unknown, type: string): boolean => {
  if (type === 'null') return value === null;
  if (type === 'object') return isRecord(value);
  if (type === 'array') return Array.isArray(value);
  if (type === 'integer') return Number.isInteger(value);
  if (type === 'number') return typeof value === 'number' && Number.isFinite(value);
  return typeof value === type;
};

const isValidUtcTimestamp = (value: unknown): boolean => {
  if (typeof value !== 'string') return false;
  const match = utcTimestampPattern.exec(value);
  if (!match) return false;

  const [, yearText, monthText, dayText, hourText, minuteText, secondText, fractionText] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const hour = Number(hourText);
  const minute = Number(minuteText);
  const second = Number(secondText);
  const millisecond = Number((fractionText ?? '').padEnd(3, '0').slice(0, 3) || '0');
  if (month < 1 || month > 12 || day < 1 || day > 31 || hour > 23 || minute > 59 || second > 59)
    return false;

  const date = new Date(0);
  date.setUTCFullYear(year, month - 1, day);
  date.setUTCHours(hour, minute, second, millisecond);
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day &&
    date.getUTCHours() === hour &&
    date.getUTCMinutes() === minute &&
    date.getUTCSeconds() === second
  );
};

const isSafeEvidenceUri = (value: unknown): boolean => {
  if (typeof value !== 'string' || value.includes('@')) return false;
  if (value.startsWith('s3://')) return /^s3:\/\/[^\s/]+\/[^\s]+$/.test(value);
  if (!value.startsWith('https://')) return false;
  try {
    const url = new URL(value);
    return (
      url.protocol === 'https:' &&
      url.username === '' &&
      url.password === '' &&
      url.hostname.length > 0 &&
      url.pathname.length > 1
    );
  } catch {
    return false;
  }
};

const validateValue = (value: unknown, schema: JsonSchema, path: string): ValidationError[] => {
  const errors: ValidationError[] = [];
  const schemaTypes = schema.type ? (Array.isArray(schema.type) ? schema.type : [schema.type]) : [];
  if (schemaTypes.length > 0 && !schemaTypes.some((type) => typeMatches(value, type))) {
    return [{ path, message: `类型必须是 ${schemaTypes.join(' 或 ')}` }];
  }
  if (schema.const !== undefined && value !== schema.const)
    errors.push({ path, message: '常量值不匹配' });
  if (schema.enum && !schema.enum.includes(value)) errors.push({ path, message: '枚举值不合法' });
  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength)
      errors.push({ path, message: '长度过短' });
    if (schema.pattern && !new RegExp(schema.pattern).test(value))
      errors.push({ path, message: '格式不合法' });
    if (schema.pattern === utcTimestampPattern.source && !isValidUtcTimestamp(value))
      errors.push({ path, message: '不是有效的 UTC 日历时间' });
  }
  if (typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum)
      errors.push({ path, message: '小于最小值' });
    if (schema.maximum !== undefined && value > schema.maximum)
      errors.push({ path, message: '大于最大值' });
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems)
      errors.push({ path, message: '元素数量过少' });
    if (
      schema.uniqueItems &&
      new Set(value.map((item) => JSON.stringify(item))).size !== value.length
    )
      errors.push({ path, message: '包含重复元素' });
    if (schema.items)
      value.forEach((item, index) =>
        errors.push(...validateValue(item, schema.items as JsonSchema, `${path}[${index}]`)),
      );
  }
  if (isRecord(value)) {
    for (const required of schema.required ?? []) {
      if (!Object.hasOwn(value, required) || value[required] === undefined)
        errors.push({ path: `${path}.${required}`, message: '字段必填' });
    }
    if (schema.additionalProperties === false) {
      for (const key of Object.keys(value))
        if (!schema.properties || !Object.hasOwn(schema.properties, key))
          errors.push({ path: `${path}.${key}`, message: '不允许的字段' });
    }
    for (const [key, child] of Object.entries(schema.properties ?? {})) {
      if (value[key] !== undefined)
        errors.push(...validateValue(value[key], child, `${path}.${key}`));
    }
  }
  if (schema.not && validateValue(value, schema.not, path).length === 0)
    errors.push({ path, message: '不满足互斥条件' });
  if (schema.oneOf) {
    const schemaWithoutOneOf = { ...schema };
    delete schemaWithoutOneOf.oneOf;
    const matches = schema.oneOf.filter(
      (branch) =>
        validateValue(value, { ...schemaWithoutOneOf, ...branch, additionalProperties: true }, path)
          .length === 0,
    );
    if (matches.length !== 1) errors.push({ path, message: '不匹配唯一的业务变体' });
  }
  return errors;
};

export const validateContract = (name: ContractName, value: unknown): ValidationResult => {
  const schema = contractSchemas[name];
  const errors = validateValue(value, schema, '$');

  if (
    name === 'diagnosticEvent' &&
    isRecord(value) &&
    typeof value.evidenceUri === 'string' &&
    !isSafeEvidenceUri(value.evidenceUri)
  ) {
    errors.push({ path: '$.evidenceUri', message: '证据地址必须是无凭据的受控 S3 或 HTTPS 地址' });
  }
  if (
    name === 'diagnosticQuery' &&
    isRecord(value) &&
    typeof value.from === 'string' &&
    typeof value.to === 'string' &&
    value.from >= value.to
  ) {
    errors.push({ path: '$.to', message: '必须晚于 from' });
  }
  if (name === 'edgeStatusReport' && isRecord(value) && isRecord(value.resources)) {
    for (const [resourceName, resource] of Object.entries(value.resources)) {
      if (!isRecord(resource)) continue;
      if (resource.status === 'available' && typeof resource.value !== 'number')
        errors.push({
          path: `$.resources.${resourceName}.value`,
          message: 'available 时必须是数字',
        });
      if (resource.status !== 'available' && resource.value !== null)
        errors.push({ path: `$.resources.${resourceName}.value`, message: '不可用时必须是 null' });
    }
  }
  if (name === 'idempotentEventResponse' && isRecord(value)) {
    const outcome = value.outcome;
    const created = value.created;
    const hasError = Object.hasOwn(value, 'error') && value.error !== undefined;
    if (outcome === 'ACCEPTED' && (created !== true || hasError))
      errors.push({ path: '$', message: 'ACCEPTED 必须 created=true 且不能携带 error' });
    if (outcome === 'DUPLICATE_ACCEPTED' && (created !== false || hasError))
      errors.push({ path: '$', message: 'DUPLICATE_ACCEPTED 必须 created=false 且不能携带 error' });
    if (
      outcome === 'CONFLICT' &&
      (created !== false || !isRecord(value.error) || value.error.code !== 'IDEMPOTENCY_CONFLICT')
    )
      errors.push({
        path: '$',
        message: 'CONFLICT 必须 created=false 且使用 IDEMPOTENCY_CONFLICT',
      });
  }

  return errors.length > 0 ? { valid: false, errors } : { valid: true };
};

export const identifierSchemaExample = {
  type: 'object',
  required: ['assetId', 'terminalId', 'edgeId', 'eventId'],
  properties: {
    assetId: { type: 'string', description: '被诊断的物理资产。' },
    terminalId: { type: 'string', description: '采集数据的感知终端。' },
    edgeId: { type: 'string', description: '接收数据的边端节点。' },
    eventId: { type: 'string', description: '诊断事件的全链路标识。' },
  },
};
