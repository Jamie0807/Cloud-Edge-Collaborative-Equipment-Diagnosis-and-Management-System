import { identifierSchemaExample } from '../src/identifiers';
import { describe, expect, it } from 'vitest';

describe('标识契约示例', () => {
  it('保留四个语义独立的跨服务标识', () => {
    expect(Object.keys(identifierSchemaExample.properties)).toEqual([
      'assetId',
      'terminalId',
      'edgeId',
      'eventId',
    ]);
  });
});
