// Pure panel logic (no DOM): local stop word and the AI-mode permit/lease rules.
// The MacBook executor (A3 Lite) mirrors the same rules; the ESP32 core keeps its own 100 ms freshness limit.

export const LEASE_PERIOD_MS = 50;
export const LEASE_TIMEOUT_MS = 100;
const STOP_WORDS = new Set(['dur', 'durdur', 'stop', 'kes']);

/** True when the text must stop the robot locally, without going to the AI. */
export function isStopCommand(text) {
  return String(text)
    .toLocaleLowerCase('tr')
    .split(/[^\p{L}]+/u)
    .some((word) => STOP_WORDS.has(word));
}

/** AI mode is allowed only with the switch on and this page visible and focused. */
export class AiPermit {
  constructor() {
    this.switchOn = false;
    this.visible = false;
    this.focused = false;
  }

  setSwitch(on) {
    this.switchOn = Boolean(on);
  }

  setPage({ visible, focused }) {
    this.visible = Boolean(visible);
    this.focused = Boolean(focused);
  }

  /** Joystick/keyboard driving takes over: AI mode drops at once. */
  operatorTookOver() {
    this.switchOn = false;
  }

  allowed() {
    return this.switchOn && this.visible && this.focused;
  }
}

export const leaseDue = (lastSentMs, nowMs) => nowMs - lastSentMs >= LEASE_PERIOD_MS;
export const leaseFresh = (lastRenewMs, nowMs) => nowMs - lastRenewMs <= LEASE_TIMEOUT_MS;
