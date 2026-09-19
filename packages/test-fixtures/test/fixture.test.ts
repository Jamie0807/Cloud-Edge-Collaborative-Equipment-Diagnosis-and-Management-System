import { healthFixture } from '../src/health';
import { describe, expect, it } from 'vitest';

describe('健康夹具', () => {
  it('保持确定性', () => {
    expect(healthFixture).toEqual({ status: 'ok' });
  });
});
