import { healthFixture } from '../src/health.js';
import { describe, expect, it } from 'vitest';

describe('health fixture', () => {
  it('is deterministic', () => {
    expect(healthFixture).toEqual({ status: 'ok' });
  });
});
