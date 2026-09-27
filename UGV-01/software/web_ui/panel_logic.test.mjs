// node --test software/web_ui/panel_logic.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { AiPermit, LEASE_PERIOD_MS, leaseDue, leaseFresh, isStopCommand } from './panel_logic.mjs';

test('stop words are handled locally, before any AI', () => {
  for (const text of ['dur', 'Dur!', 'DUR lütfen', 'stop', 'STOP.', 'hemen dur', 'Durdur', 'kes']) {
    assert.equal(isStopCommand(text), true, text);
  }
  for (const text of ['durum nedir', 'kırmızı küpü al', 'duruş', 'keske', '']) {
    assert.equal(isStopCommand(text), false, text);
  }
});

test('AI mode needs switch, visible page and focus; operator input drops it', () => {
  const p = new AiPermit();
  assert.equal(p.allowed(), false);
  p.setSwitch(true);
  p.setPage({ visible: true, focused: false });
  assert.equal(p.allowed(), false);
  p.setPage({ visible: true, focused: true });
  assert.equal(p.allowed(), true);
  p.setPage({ visible: false, focused: true });
  assert.equal(p.allowed(), false);
  p.setPage({ visible: true, focused: true });
  p.operatorTookOver();
  assert.equal(p.allowed(), false);
  assert.equal(p.switchOn, false);
});

test('lease is sent every 50 ms and is stale after 100 ms', () => {
  assert.equal(LEASE_PERIOD_MS, 50);
  assert.equal(leaseDue(0, 49), false);
  assert.equal(leaseDue(0, 50), true);
  assert.equal(leaseFresh(0, 100), true);
  assert.equal(leaseFresh(0, 101), false);
});
