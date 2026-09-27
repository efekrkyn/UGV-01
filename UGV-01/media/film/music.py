"""UGV-01 film score v2: an original 1960s big-band swing chart, synthesised from scratch (no samples, no borrowed
melody): walking upright bass, ride and brushes, finger snaps, muted-trumpet lead, 4-way brass and sax voicings with
fall-offs, vibraphone bridge, a key change up a whole step for the shout chorus and a button ending.

Reads timeline.json (tempo, hits, the "dur" silence, voice cues) and writes out/score.wav (48 kHz stereo). Voices are
macOS `say` Yelda: the operator as spoken, the robot pitched up and lightly robotised.
"""
import json
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / 'timeline.json').read_text())
SR = 48000
BEAT = 60 / T['bpm']
BAR = 4 * BEAT
DUR = T['duration_s']
N = int(SR * (DUR + 3))
dry, send, voice_bus = np.zeros((N, 2)), np.zeros((N, 2)), np.zeros((N, 2))
rng = np.random.default_rng(1962)
SWING = 2 / 3  # the "and" of a swung beat


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(sig, t, pan=0.0, gain=1.0, verb=0.2, bus=None):
    i = int(round(t * SR))
    if i >= N or i < 0 or not len(sig):
        return
    sig = sig[:N - i] * gain
    left, right = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    target = dry if bus is None else bus
    target[i:i + len(sig), 0] += sig * left
    target[i:i + len(sig), 1] += sig * right
    send[i:i + len(sig), 0] += sig * left * verb
    send[i:i + len(sig), 1] += sig * right * verb


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'high', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'low', fs=SR, output='sos'), x)


def noise(n):
    return rng.standard_normal(n)


def tvec(sec):
    return np.arange(int(SR * sec)) / SR


# ---- rhythm section
def upright(m, dur, vel=0.7):
    t = tvec(dur + 0.35)
    f = hz(m) * (1 + 0.012 * np.exp(-t / 0.03))  # the string settles after the pluck
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = sum((1 / k ** 1.5) * np.exp(-t * (1.6 + 1.3 * k)) * np.sin(k * ph) for k in range(1, 8))
    thump = lp(noise(len(t)), 220) * np.exp(-t / 0.015) * 0.6
    env = np.clip(1 - (t - dur) / 0.08, 0, 1)
    return lp((out + thump) * env, 1400) * vel * 0.34


def metal(t, lo=2800, hi=10500, n=26, decay=0.6):
    """Band-limited cymbal: inharmonic sine partials with their own decays (no aliasing square waves)."""
    out = np.zeros(len(t))
    for f in np.sort(rng.uniform(lo, hi, n)):
        out += rng.uniform(0.4, 1.0) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.3)) * np.exp(-t / (decay * rng.uniform(0.5, 1.2)))
    return out / n


def ride(vel=0.5, bell=False):
    t = tvec(1.4)
    body = metal(t, 3000, 9500, 26, 0.55)
    ping = np.sin(2 * np.pi * (3350 if bell else 3100) * t) * np.exp(-t / (0.35 if bell else 0.1))
    wash = lp(hp(noise(len(t)), 5500), 11000) * np.exp(-t / 0.25)
    return (body * 0.36 + ping * 0.06 + wash * 0.01) * vel


def crash(vel=0.8):
    t = tvec(2.8)
    body = metal(t, 2200, 10000, 40, 1.1) * 0.9 + lp(hp(noise(len(t)), 3000), 11000) * np.exp(-t / 0.8) * 0.12
    return body * vel * 0.3


def hat_foot(vel=0.4):
    t = tvec(0.08)
    return lp(hp(noise(len(t)), 6000), 11000) * np.exp(-t / 0.016) * vel * 0.3


def kick(vel=0.5):
    t = tvec(0.4)
    f = 50 + 40 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2) * vel * 0.6


def snare(vel=0.5):
    t = tvec(0.3)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    rattle = bp(noise(len(t)), 1500, 7000) * np.exp(-t / 0.12)
    return (tone * 0.4 + rattle) * vel * 0.3


def brush_slap(vel=0.4):
    t = tvec(0.25)
    return bp(noise(len(t)), 900, 5500) * np.exp(-t / 0.07) * vel * 0.25


def brush_swish(dur, vel=0.25):
    t = tvec(dur)
    return bp(noise(len(t)), 800, 4200) * np.sin(np.pi * t / dur) ** 1.5 * vel * 0.12


def snap(vel=0.6):
    t = tvec(0.1)
    click = np.zeros(len(t))
    click[:30] = np.hanning(30)
    return (bp(noise(len(t)), 1800, 3600) * np.exp(-t / 0.012) + click * 0.4) * vel * 0.5


def roll(dur, vel0=0.1, vel1=0.8):
    out = np.zeros(int(SR * (dur + 0.3)))
    step = BEAT / 8
    for k in range(int(dur / step)):
        v = vel0 + (vel1 - vel0) * (k * step / dur) ** 1.6
        s = snare(v * (0.85 + 0.3 * rng.random()))
        i = int(k * step * SR)
        out[i:i + len(s)] += s[:len(out) - i]
    return out


# ---- horns, piano, vibes, strings
def horn(m, dur, vel=0.6, kind='tpt', fall=False):
    t = tvec(dur + (0.45 if fall else 0.12))
    vib = {'tpt': 14, 'tbn': 10, 'sax': 22, 'mute': 12}[kind]
    cents = -35 * np.exp(-t / 0.035) + vib * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.22) / 0.2, 0, 1)
    if fall:
        cents = cents - 900 * np.clip((t - dur) / 0.4, 0, 1) ** 1.6
    f = hz(m) * 2 ** (cents / 1200)
    ph = 2 * np.pi * np.cumsum(f) / SR
    bright = vel * (0.62 + 0.38 * np.exp(-t / 0.06))
    base = {'tpt': 2.35, 'tbn': 2.6, 'sax': 2.05, 'mute': 2.2}[kind]
    out = np.zeros(len(t))
    for k in range(1, 18):
        if k * hz(m) > 12000:
            break
        amp = np.exp(-(base - 1.45 * bright) * math.log(k))
        if kind == 'sax' and k % 2 == 0:
            amp = amp * 0.6
        out += amp * np.sin(k * ph)
    att = {'tpt': 0.014, 'tbn': 0.02, 'sax': 0.028, 'mute': 0.012}[kind]
    rel_end = dur + (0.4 if fall else 0.06)
    env = np.minimum(1, t / att) * np.clip((rel_end - t) / (0.4 if fall else 0.06), 0, 1)
    out = out * env + bp(noise(len(t)), 1500, 6000) * env * 0.02  # breath
    if kind == 'mute':
        out = bp(out, 1100, 4200) * 2.2
    return lp(out, 9000) * vel * {'tpt': 0.075, 'tbn': 0.085, 'sax': 0.07, 'mute': 0.1}[kind]


def piano(m, dur, vel=0.5):
    f0, t = hz(m), tvec(dur + 1.0)
    out = np.zeros(len(t))
    for k in range(1, 10):
        fk = k * f0 * math.sqrt(1 + 0.0003 * k * k)
        if fk > 14000:
            break
        out += (1 / k ** 1.4) * np.exp(-(0.8 + 0.6 * k) * (f0 / 262) ** 0.35 * t) * np.sin(2 * np.pi * fk * t)
    env = np.minimum(1, t / 0.004) * np.clip(1 - (t - dur) / 0.12, 0, 1)
    return out * env * vel * 0.16


def vibes(m, dur, vel=0.5):
    t = tvec(dur + 1.6)
    f = hz(m)
    out = sum(a * np.exp(-d * t) * np.sin(2 * np.pi * f * r * t) for r, a, d in ((1, 1, 1.3), (3.93, 0.25, 3.5), (9.2, 0.07, 8)))
    trem = 1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.6 * t))
    return out * trem * np.minimum(1, t / 0.002) * vel * 0.16


def strings(notes, dur, vel=0.5):
    t = tvec(dur + 2.0)
    out = np.zeros(len(t))
    for m in notes:
        for c in (-7, 0, 7):
            f = hz(m) * 2 ** (c / 1200)
            ph = 2 * np.pi * f * (t + 0.004 * np.sin(2 * np.pi * 5.2 * t) / (2 * np.pi * 5.2))
            out += sum(np.sin(k * ph) / k for k in range(1, 12) if k * f < 10000)
    env = np.minimum(1, t / 0.8) * np.clip(1 - (t - dur) / 2.0, 0, 1)
    return lp(out, 3000) * env * vel * 0.03 / len(notes) ** 0.5


# ---- harmony
PC = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
QUAL = {'6': [0, 4, 7, 9], '69': [0, 4, 7, 9, 14], 'm7': [0, 3, 7, 10], '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11],
        'm6': [0, 3, 7, 9]}


def parse(ch):
    root = ch[:2] if len(ch) > 1 and ch[1] in 'b#' else ch[:1]
    return PC[root], QUAL[ch[len(root):]]


def transpose_name(ch, n):
    root = ch[:2] if len(ch) > 1 and ch[1] in 'b#' else ch[:1]
    names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    return names[(PC[root] + n) % 12] + ch[len(root):]


A_F = [['F6'], ['Dm7'], ['Gm7'], ['C7'], ['Am7'], ['D7'], ['Gm7', 'C7'], ['F6']]
BUILD = [['Gm7', 'C7'], ['Am7', 'D7'], ['Gm7', 'C7'], ['F6', 'C7']]
B_F = [['Bbmaj7'], ['Bbm6'], ['Am7'], ['D7'], ['Gm7'], ['C7'], ['F6'], ['F6']]
A_G = [[transpose_name(c, 2) for c in bar] for bar in A_F]
CHART = ([['F69'], ['F69'], ['F69'], ['C7']] + A_F + A_F + B_F + BUILD + A_F[:6] + A_G[:7]  # 50 bars, see timeline.json
         + [['Am7', 'D7'], ['G69'], ['G69'], ['G69'], ['G69']])


def chord_at(bar, beat=0.0):
    chords = CHART[min(bar, len(CHART) - 1)]
    return parse(chords[min(int(beat // (4 / len(chords))), len(chords) - 1)])


def voicing(root, qual, top, n=4):
    """n chord tones at and below `top` (close position): the top voice sings the melody."""
    tones = sorted({(root + q) % 12 for q in qual})
    out, m = [top], top - 1
    while len(out) < n and m > top - 13:
        if m % 12 in tones:
            out.append(m)
        m -= 1
    return out


# ---- melodies: (bar, beat, beats, midi[, 'fall'])
MEL_A = [(0, .667, .333, 72), (0, 1, 1, 74), (0, 2, .667, 77), (0, 2.667, 1.333, 81),
         (1, 0, 1.5, 79), (1, 2, .667, 77), (1, 2.667, 1.333, 74),
         (2, 0, .667, 70), (2, .667, .333, 72), (2, 1, 1, 74), (2, 2, .667, 77), (2, 2.667, 1.333, 76),
         (3, 0, 2, 79), (3, 2.667, 1.333, 76),
         (4, 0, .667, 72), (4, .667, .333, 76), (4, 1, 1, 79), (4, 2, 2, 81),
         (5, 0, .667, 78), (5, .667, 1.333, 81), (5, 2, .667, 84), (5, 2.667, 1.333, 81),
         (6, 0, 1, 79), (6, 1, 1, 77), (6, 2, .667, 74), (6, 2.667, 1.333, 76),
         (7, 0, 2.5, 77, 'fall')]
MEL_B = [(0, 0, .667, 74), (0, .667, .333, 77), (0, 1, 1.5, 81), (0, 2.667, 1.333, 79),
         (1, 0, .667, 73), (1, .667, .333, 77), (1, 1, 2, 79),
         (2, 0, .667, 76), (2, .667, 1.333, 72), (2, 2, 2, 79),
         (3, 0, .667, 78), (3, .667, .333, 81), (3, 1, 2, 84),
         (4, 0, 1, 82), (4, 1, 1, 81), (4, 2, 2, 77),
         (5, 0, .667, 76), (5, .667, 1.333, 79), (5, 2, 2, 82),
         (6, 0, 3, 81)]


def play_melody(mel, bar0, shift=0, kind='mute', vel=0.6, harmonise=0, pan=-0.2, bars=8):
    for note in mel:
        b, beat, beats, m = note[:4]
        if b >= bars:
            continue
        fall = len(note) > 4
        m += shift
        t = at(bar0 + b, beat)
        dur = beats * BEAT * 0.92
        if harmonise:
            root, qual = chord_at(bar0 + b, beat)
            for k, v in enumerate(voicing(root, qual, m, harmonise)):
                jitter = rng.normal(0, 0.005)
                put(horn(v, dur, vel * (1 if k == 0 else 0.8), 'tpt', fall), t + jitter, -0.3 + 0.12 * k, verb=0.22)
                put(horn(v - 12, dur, vel * 0.75, 'tbn', fall), t + jitter, 0.35 - 0.1 * k, verb=0.22)
        else:
            put(horn(m, dur, vel, kind, fall), t, pan, verb=0.3)


def tutti(t, root_name, dur=0.5, vel=0.9, fall=True, top=81):
    root, qual = parse(root_name)
    for k, v in enumerate(voicing(root, qual, top, 5)):
        put(horn(v, dur, vel, 'tpt', fall and k == 0), t + rng.normal(0, 0.004), -0.3 + 0.12 * k, verb=0.25)
        put(horn(v - 12, dur, vel * 0.85, 'tbn', False), t + rng.normal(0, 0.004), 0.35 - 0.1 * k, verb=0.25)
        put(horn(v - 5, dur, vel * 0.6, 'sax', False), t + rng.normal(0, 0.004), 0.1, verb=0.25)


# ---- arrangement
def walking_bass(bar0, bar1, two_feel=False, vel=0.7):
    for bar in range(bar0, bar1):
        chords = CHART[bar]
        per = 4 // len(chords)
        for ci, name in enumerate(chords):
            root, qual = parse(name)
            nxt = parse(CHART[bar + 1][0] if ci == len(chords) - 1 and bar + 1 < len(CHART) else chords[min(ci + 1, len(chords) - 1)])[0]
            r = 28 + (root - 4) % 12  # E1 .. D#2
            n_next = 28 + (nxt - 4) % 12
            if per == 4:
                line = [r, r + qual[1], r + 7, n_next + (1 if n_next < r + 7 else -1)]
            else:
                line = [r, n_next + (1 if n_next <= r else -1)]
            if two_feel:
                line = line[::2] if per == 4 else line[:1]
            step = per / len(line)
            for k, m in enumerate(line):
                put(upright(m, step * BEAT * 0.95, vel), at(bar, ci * per + k * step), 0.0, verb=0.08)


def swing_kit(bar0, bar1, sticks=False, snaps=False, vel=0.6):
    for bar in range(bar0, bar1):
        for beat, v in ((0, 0.8), (1, 1.0), (1 + SWING, 0.6), (2, 0.8), (3, 1.0), (3 + SWING, 0.6)):
            put(ride(vel * v, bell=False), at(bar, beat), 0.35, verb=0.12)
        for beat in (1, 3):
            put(hat_foot(0.5), at(bar, beat), -0.3, verb=0.05)
            if snaps:
                put(snap(0.7), at(bar, beat), -0.15, verb=0.25)
            if sticks:
                put(snare(0.42 * vel / 0.6), at(bar, beat), -0.1, verb=0.15)
        for beat in range(4):
            put(kick(0.17), at(bar, beat), 0.0, verb=0.03)
        if sticks and bar % 4 == 3:  # fill into the next phrase
            for k, beat in enumerate((2, 2 + SWING, 3, 3 + SWING / 2, 3 + SWING)):
                put(snare(0.35 + 0.12 * k), at(bar, beat), -0.1, verb=0.15)


def brushes(bar0, bar1):
    for bar in range(bar0, bar1):
        for beat in range(4):
            put(brush_swish(BEAT * 0.95, 0.35), at(bar, beat), -0.1, verb=0.1)
        for beat in (1, 3):
            put(brush_slap(0.6), at(bar, beat), -0.1, verb=0.12)
            put(snap(0.55), at(bar, beat), 0.2, verb=0.3)
        put(ride(0.25, bell=True), at(bar, 0), 0.35, verb=0.15)


def piano_comp(bar0, bar1, vel=0.4):
    for bar in range(bar0, bar1):
        patterns = [(1 + SWING,), (0, 2 + SWING), (1 + SWING, 3), (2 + SWING,)]
        for beat in patterns[rng.integers(len(patterns))]:
            root, qual = chord_at(bar, beat)
            for k, iv in enumerate(qual[1:4]):  # shell: 3rd, 5th/6th, 7th around middle C
                put(piano(60 + (root + iv - 60) % 12 + (12 if k == 2 and iv < 7 else 0), BEAT * 0.3, vel), at(bar, beat), -0.35, verb=0.2)


def sax_pads(bar0, bar1, vel=0.35):
    for bar in range(bar0, bar1):
        root, qual = chord_at(bar, 0)
        for k, v in enumerate(voicing(root, qual, 67, 4)):
            put(horn(v, BAR * 0.95, vel, 'sax'), at(bar, 0), 0.1 + 0.05 * k, verb=0.3)


def compose():
    # intro (0-4): snare roll into two band hits, then a walk-up into the groove
    put(roll(at(2) - 0.05, 0.08, 0.9), 0.0, -0.1, verb=0.2)
    swell = hp(noise(int(at(2) * SR)), 3000) * np.linspace(0, 1, int(at(2) * SR)) ** 3 * 0.05
    put(swell, 0.0, 0.2, verb=0.3)
    for t in (T['hits'][0][0], T['hits'][1][0]):
        tutti(t, 'F69', dur=0.7, vel=0.95)
        put(crash(0.9), t, 0.3, verb=0.3)
        put(kick(0.9), t)
        put(upright(29, 0.6, 0.9), t)
    for k, m in enumerate((36, 38, 40)):
        put(upright(m, BEAT * 0.9, 0.8), at(3, 1 + k), verb=0.08)
    # groove (4-12): muted trumpet lead, snaps, soft saxes from bar 8
    walking_bass(4, 12)
    swing_kit(4, 12, snaps=True, vel=0.5)
    piano_comp(4, 12)
    play_melody(MEL_A, 4, kind='mute', vel=0.7)
    sax_pads(8, 12, 0.28)
    # engineering (12-20): sax soli on the tune, brass stabs on the hits
    walking_bass(12, 20)
    swing_kit(12, 20, sticks=True, vel=0.6)
    piano_comp(12, 20)
    for note in MEL_A:
        b, beat, beats, m = note[:4]
        root, qual = chord_at(12 + b, beat)
        for k, v in enumerate(voicing(root, qual, m - 12, 4)):
            put(horn(v, beats * BEAT * 0.9, 0.55, 'sax', len(note) > 4 and k == 0), at(12 + b, beat), 0.1 + 0.06 * k, verb=0.25)
    # AI + voice (20-32): lounge two-feel, brushes, snaps, vibraphone bridge, a muted build towards "dur"
    walking_bass(20, 32, two_feel=True, vel=0.6)
    brushes(20, 32)
    for b, beat, beats, m in MEL_B:
        put(vibes(m, beats * BEAT, 0.55), at(20 + b, beat), 0.35, verb=0.35)
    sax_pads(20, 28, 0.18)
    for bar in range(28, 31):
        for beat in (0, 1 + SWING):
            tutti(at(bar, beat), CHART[bar][0 if beat < 2 else -1], dur=0.2, vel=0.4 + 0.08 * (bar - 28), fall=False, top=76 + 2 * (bar - 28))
    # safety (32-38): the band is back, open brass on the tune; its last bar (D7) is the pivot into G
    walking_bass(32, 38)
    swing_kit(32, 38, sticks=True, vel=0.65)
    piano_comp(32, 38)
    play_melody(MEL_A, 32, harmonise=4, vel=0.62, bars=6)
    # shout chorus in G (38-45): full band, tune harmonised, sax riffs, crashes on the phrase heads
    walking_bass(38, 46, vel=0.8)
    swing_kit(38, 46, sticks=True, vel=0.75)
    piano_comp(38, 46, 0.45)
    play_melody(MEL_A, 38, shift=2, harmonise=4, vel=0.8, bars=7)
    for bar in range(38, 45):
        if bar in (38, 42):
            put(crash(0.7), at(bar), 0.3, verb=0.25)
        root, qual = chord_at(bar, 2 + SWING)
        for v in voicing(root, qual, 67, 3):
            put(horn(v, BEAT * 0.5, 0.55, 'sax'), at(bar, 2 + SWING), 0.15, verb=0.2)
            put(horn(v, BEAT * 0.4, 0.5, 'sax'), at(bar, 3 + SWING), 0.15, verb=0.2)
    # tag (45) and the button (46), then a quiet G6/9 to the end
    for beat, name in ((0, 'Am7'), (2, 'D7')):
        tutti(at(45, beat), name, dur=0.35, vel=0.8, fall=False, top=81 if beat == 0 else 78)
    btn = [t for t, kind in T['hits'] if kind == 'button'][0]
    tutti(btn, 'G69', dur=0.9, vel=1.0, fall=True, top=83)
    put(crash(1.0), btn, 0.3, verb=0.4)
    put(kick(1.0), btn)
    put(upright(31, 0.8, 0.9), btn)
    put(strings([55, 59, 64, 67, 69, 74], DUR - btn - 1.0, 0.5), btn + 0.8, verb=0.5)
    for k, m in enumerate((79, 83, 86, 88, 91)):
        put(vibes(m, 1.2, 0.4), btn + 1.2 + 0.3 * k, 0.35, verb=0.45)
    put(ride(0.3, bell=True), btn + 2.4, 0.35, verb=0.4)
    # hits the picture cuts on (engineering stats, safety cues, title); ticks are soft vibes/muted stabs
    for t, kind in T['hits']:
        bar = int(t // BAR)
        name = CHART[min(bar, len(CHART) - 1)][0]
        if kind == 'big' and t > 6:
            tutti(t, name, dur=0.55, vel=0.95, fall=True, top=84 if bar >= 38 else 81)
            put(crash(0.85), t, 0.3, verb=0.3)
            put(kick(0.9), t)
        elif kind == 'stab':
            tutti(t, name, dur=0.22, vel=0.75, fall=False, top=79)
            put(snare(0.6), t, -0.1, verb=0.15)
        elif kind == 'tick':
            root, qual = parse(name)
            for v in voicing(root, qual, 84, 3):
                put(vibes(v, 0.4, 0.5), t, 0.35, verb=0.3)
            put(horn(79, 0.15, 0.4, 'mute'), t, -0.2, verb=0.2)
        elif kind == 'stop':
            tutti(t, name, dur=0.18, vel=0.9, fall=False, top=81)
            put(crash(0.6)[: int(0.12 * SR)], t, 0.3, verb=0.05)  # choked


# ---- voices
def say(text, robot):
    with tempfile.TemporaryDirectory() as tmp:
        aiff, wav = Path(tmp) / 'v.aiff', Path(tmp) / 'v.wav'
        subprocess.run(['say', '-v', 'Yelda', '-r', '165' if robot else '175', '-o', str(aiff), text], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-ac', '1', '-ar', str(SR), str(wav)], check=True)
        _, x = wavfile.read(wav)
    x = x.astype(np.float64) / 32768
    if robot:
        x = signal.resample(x, int(len(x) / 1.26))  # about four semitones up: small robot
        t = np.arange(len(x)) / SR
        x = x * (0.85 + 0.15 * np.sin(2 * np.pi * 34 * t))
        chorus = np.concatenate([np.zeros(int(0.011 * SR)), signal.resample(x, int(len(x) * 0.994))])[:len(x)]
        x = bp(x + 0.35 * chorus, 260, 6500)
    else:
        x = bp(x, 120, 9000)
    return x / (np.max(np.abs(x)) + 1e-9) * (0.42 if robot else 0.5)


def main():
    compose()
    for t, text, who in T['voice']:
        put(say(text, who == 'robot'), t, 0.0 if who == 'robot' else -0.05, verb=0.12, bus=voice_bus)
    ir_t = np.arange(int(2.2 * SR)) / SR
    wet = np.zeros_like(send)
    for ch in range(2):
        ir = lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.5), 6000, 1)
        ir[: int(0.022 * SR)] = 0
        wet[:, ch] = signal.fftconvolve(send[:, ch], ir / np.sqrt(np.sum(ir ** 2)))[:N]
    music = dry + wet * 0.5
    t = np.arange(N) / SR
    s0, s1 = T['silence']  # "dur": the band stops dead, comes back on the downbeat
    gate = np.clip((s0 + 0.14 - t) / 0.12, 0, 1) + np.clip((t - s1 + 0.02) / 0.02, 0, 1)
    music *= np.clip(gate, 0, 1)[:, None]
    level = np.abs(voice_bus).max(axis=1)
    duck = 1 - 0.5 * np.clip(signal.sosfiltfilt(signal.butter(1, 3, 'low', fs=SR, output='sos'), level) / 0.1, 0, 1)
    mix = music * duck[:, None] + voice_bus
    mix = signal.sosfilt(signal.butter(2, 13000, 'low', fs=SR, output='sos'), mix, axis=0)  # tame the top octave
    mix = signal.sosfilt(signal.butter(2, 35, 'high', fs=SR, output='sos'), mix, axis=0)  # and the rumble
    mix *= np.clip((DUR - t) / 2.5, 0, 1)[:, None] * np.clip(t / 0.05, 0, 1)[:, None]
    mix = np.tanh(mix / (np.max(np.abs(mix)) + 1e-9) * 1.8) / np.tanh(1.8) * 0.89
    out = HERE / 'out'
    out.mkdir(exist_ok=True)
    wavfile.write(out / 'score.wav', SR, (mix[: int(SR * DUR)] * 32767).astype(np.int16))
    print(f'wrote {out / "score.wav"}: {DUR} s')


if __name__ == '__main__':
    main()
