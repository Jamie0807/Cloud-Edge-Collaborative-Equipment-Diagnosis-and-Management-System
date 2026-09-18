import { identifierSchemaExample } from '../src/identifiers.js';
import { describe, expect, it } from 'vitest';

describe('identifier schema', () => {
  it('keeps all cross-service identifiers distinct', () => {
    expect(Object.keys(identifierSchemaExample.properties)).toEqual([
      'assetId',
      'terminalId',
      'edgeId',
      'eventId',
    ]);
  });
});
