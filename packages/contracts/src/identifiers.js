export const identifierSchemaExample = {
  type: 'object',
  required: ['assetId', 'terminalId', 'edgeId', 'eventId'],
  properties: {
    assetId: { type: 'string', description: 'The diagnosed physical asset.' },
    terminalId: { type: 'string', description: 'The sensing terminal.' },
    edgeId: { type: 'string', description: 'The receiving edge service.' },
    eventId: { type: 'string', description: 'The diagnostic event.' },
  },
};
