"""Robot crooner vocals for the UGV-01 film (vocal version, `python3 music.py --vocal`).

The lyrics in README.md are spoken word by word by macOS `say` (Daniel), each word stretched onto its notes of an
original vocal melody, then sung through a channel vocoder whose carrier follows that melody (portamento, vibrato
on long notes): the robot itself does the singing. The intro line is spoken by an announcer voice (Ralph).
"""
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
SINGER, ANNOUNCER = 'Daniel', 'Ralph'

# (bar, beat, word, [(midi, beats), ...]); chords per bar are music.CHART. Verses in F, chorus in G after the pivot.
VERSE1 = [
    (4, 0, 'four', [(60, 1)]), (4, 1, 'wheels', [(62, 1)]), (4, 2, 'rolling', [(65, .667), (69, 1.333)]),
    (5, 0, 'nice', [(67, 1)]), (5, 1, 'and', [(65, .667)]), (5, 1.667, 'slow', [(62, 2.333)]),
    (6, 0, 'every', [(58, .667), (60, .333)]), (6, 1, 'turn', [(62, 1)]), (6, 2, 'counted', [(65, .667), (64, 1.333)]),
    (7, 0, 'top', [(67, 1)]), (7, 1, 'to', [(64, .667)]), (7, 1.667, 'toe', [(60, 2.333)]),
    (8, 0, 'two', [(60, .667)]), (8, .667, 'glass', [(64, 1.333)]), (8, 2, 'eyes', [(67, 2)]),
    (9, 0, 'that', [(66, .667)]), (9, .667, 'read', [(69, 1.333)]), (9, 2, 'the', [(72, .667)]), (9, 2.667, 'room', [(69, 1.333)]),
    (10, 0, 'well', [(67, .667)]), (10, .667, 'I', [(65, .333)]), (10, 1, 'clock', [(62, 1)]), (10, 2, 'the', [(64, .667)]),
    (10, 2.667, 'cube', [(67, 1.333)]),
    (11, 0, 'before', [(65, .667), (64, .333)]), (11, 1, 'you', [(62, 1)]), (11, 2, 'do', [(65, 2)]),
]
VERSE2 = [
    (12, 0, 'ninety', [(60, .667), (62, .333)]), (12, 1, 'six', [(65, 1)]), (12, 2, 'parts', [(69, 2)]),
    (13, 0, 'not', [(67, 1)]), (13, 1, 'one', [(65, .667)]), (13, 1.667, 'to', [(64, .333)]), (13, 2, 'spare', [(62, 2)]),
    (14, 0, 'swept', [(58, .667)]), (14, .667, 'every', [(60, .333), (62, 1)]), (14, 2, 'angle', [(65, .667), (64, .333)]),
    (14, 3, 'with', [(62, .667)]), (14, 3.667, 'the', [(60, .333)]),
    (15, 0, 'greatest', [(67, .667), (64, .333)]), (15, 1, 'care', [(60, 3)]),
    (16, 0, 'seven', [(60, .667), (64, .333)]), (16, 1, 'roads', [(67, 1)]), (16, 2, 'my', [(69, .667)]), (16, 2.667, 'arm', [(67, 1.333)]),
    (17, 0, 'can', [(66, .667)]), (17, .667, 'take', [(69, 3.333)]),
    (18, 0, 'and', [(67, .667)]), (18, .667, 'not', [(65, .333)]), (18, 1, 'one', [(62, 1)]), (18, 2, 'bump', [(64, 2)]),
    (19, 0, 'for', [(62, .667)]), (19, .667, 'goodness', [(64, .333), (65, 1)]), (19, 2, 'sake', [(65, 2)]),
]
BRIDGE = [  # safety section; "alone" is held over the D7 pivot into the key change
    (32, 0, 'say', [(60, .667)]), (32, .667, 'the', [(62, .333)]), (32, 1, 'word', [(65, 1)]), (32, 2, 'stop', [(69, 2)]),
    (33, 0, 'and', [(67, .5)]), (33, .5, "I'm", [(65, .5)]), (33, 1, 'still', [(65, 1)]), (33, 2, 'as', [(62, .5)]),
    (33, 2.5, 'a', [(62, .5)]), (33, 3, 'stone', [(65, 1.667)]),
    (34, .667, 'cause', [(60, .333)]), (34, 1, 'the', [(62, .667)]), (34, 1.667, 'brakes', [(65, 1.333)]), (34, 3, 'my', [(67, .667)]),
    (34, 3.667, 'friend', [(69, 1.333)]),
    (35, 1, 'are', [(67, .667)]), (35, 1.667, 'yours', [(65, 1.333)]),
    (36, 0, 'alone', [(64, .667), (69, 7.0)]),
]
CHORUS = [  # shout chorus, G major
    (38, 0, "I'm", [(62, .667)]), (38, .667, 'small', [(67, 1.333)]), (38, 2, 'but', [(71, .667)]), (38, 2.667, "I'm", [(69, .333)]),
    (39, 0, 'something', [(71, 1), (67, 2)]),
    (40, 0, 'built', [(69, .667)]), (40, .667, 'right', [(72, 1.333)]), (40, 2, 'from', [(71, .667)]), (40, 2.667, 'the', [(69, .333)]),
    (41, 0, 'ground', [(66, 3)]),
    (42, 0, 'I', [(66, .333)]), (42, .333, 'sign', [(71, .667)]), (42, 1, 'every', [(71, .667), (69, .333)]),
    (42, 2, 'message', [(67, .667), (66, 1.333)]),
    (43, 0, 'that', [(64, .333)]), (43, .333, "I'm", [(66, .667)]), (43, 1, 'passing', [(68, .667), (71, .333)]),
    (43, 2, 'around', [(69, .667), (68, 1.333)]),
    (44, 0, 'keep', [(69, .667)]), (44, .667, 'my', [(71, .333)]), (44, 1, 'center', [(72, .667), (71, .333)]), (44, 2, 'low', [(69, 1)]),
    (44, 3, 'and', [(67, .333)]), (44, 3.333, 'my', [(66, .667)]),
    (45, 0, 'promises', [(67, .333), (69, .333), (71, .333)]), (45, 1, 'true', [(74, 2.5)]),
]
CODA = [  # after the button, soft over the strings
    (46, 1, "that's", [(62, .5)]), (46, 1.5, 'the', [(64, .5)]), (46, 2, 'little', [(67, .5), (69, .5)]),
    (46, 3, 'machine', [(71, .5), (74, 3.5)]),
]
SUNG = VERSE1 + VERSE2 + BRIDGE + CHORUS + CODA
INTRO = [(0.35, 'Ladies and gentlemen...'), (2.05, 'the little machine!')]


def tts(text, voice, rate=170):
    with tempfile.TemporaryDirectory() as tmp:
        aiff, wav = Path(tmp) / 'w.aiff', Path(tmp) / 'w.wav'
        subprocess.run(['say', '-v', voice, '-r', str(rate), '-o', str(aiff), text], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-ac', '1', '-ar', str(SR), str(wav)], check=True)
        _, x = wavfile.read(wav)
    x = x.astype(np.float64) / 32768
    loud = np.flatnonzero(np.abs(x) > 0.02 * np.max(np.abs(x)))
    return x[max(loud[0] - 240, 0): loud[-1] + 240] if len(loud) else x


def stretch(x, seconds):
    """Time-stretch x to `seconds` without changing its pitch (ffmpeg atempo, chained for large factors)."""
    factor = len(x) / SR / max(seconds, 0.05)
    chain = []
    while factor < 0.5:
        chain.append('atempo=0.5')
        factor /= 0.5
    while factor > 2.0:
        chain.append('atempo=2.0')
        factor /= 2.0
    chain.append(f'atempo={factor:.5f}')
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / 'a.wav', Path(tmp) / 'b.wav'
        wavfile.write(src, SR, (x * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-filter:a', ','.join(chain), str(dst)], check=True)
        _, y = wavfile.read(dst)
    y = y.astype(np.float64) / 32768
    n = int(seconds * SR)
    return np.pad(y, (0, max(0, n - len(y))))[:n]


def band_env(x, lo, hi, cut=35):
    b = signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
    return b, signal.sosfilt(signal.butter(2, cut, 'low', fs=SR, output='sos'), np.abs(b))


def sing(n_samples, at, beat):
    """Mono robot-crooner vocal track: vocoded words on the melody. `at(bar, beat)` gives seconds."""
    mod = np.zeros(n_samples)
    cents = np.full(n_samples, np.nan)  # pitch track (cents from A4), NaN = rest
    vib = np.zeros(n_samples)
    for bar, b, word, notes in SUNG:
        t0 = at(bar, b)
        total = sum(beats for _, beats in notes) * beat
        i0 = int(t0 * SR)
        voice = stretch(tts(word, SINGER), max(total - 0.04, 0.08))
        mod[i0:i0 + len(voice)] += voice[: max(0, n_samples - i0)]
        t = t0
        for m, beats in notes:
            j0, j1 = int(t * SR), int((t + beats * beat) * SR)
            cents[j0:j1] = (m - 69) * 100
            if (j1 - j0) / SR > 0.6:  # crooner vibrato, a little late on long notes
                tt = np.arange(j1 - j0) / SR
                vib[j0:j1] = 28 * np.sin(2 * np.pi * 5.3 * tt) * np.clip((tt - 0.25) / 0.3, 0, 1)
            t += beats * beat
    voiced = ~np.isnan(cents)
    idx = np.where(voiced, np.arange(n_samples), 0)
    np.maximum.accumulate(idx, out=idx)  # rests keep the last pitch, so each glide starts from it
    held = np.nan_to_num(cents)[idx]
    glide = signal.sosfilt(signal.butter(1, 7, 'low', fs=SR, output='sos'), held)  # portamento, ~25 ms
    f = 440.0 * 2 ** ((glide + vib) / 1200)
    phase = 2 * np.pi * np.cumsum(f) / SR
    carrier = sum(((f * k < 7500) / k) * np.sin(k * phase) for k in range(1, 48))
    carrier = carrier + 0.06 * np.random.default_rng(3).standard_normal(n_samples)
    out = np.zeros(n_samples)
    edges = np.geomspace(100, 8000, 25)
    for lo, hi in zip(edges[:-1], edges[1:]):
        _, env_m = band_env(mod, lo, hi)
        cb, env_c = band_env(carrier, lo, hi)
        out += cb * env_m / (env_c + 1e-3)
    sib = signal.sosfilt(signal.butter(2, 5000, 'high', fs=SR, output='sos'), mod) * 0.45  # s, t, k stay crisp
    out = signal.sosfilt(signal.butter(2, [120, 9000], 'band', fs=SR, output='sos'), out * 0.55 + sib)  # vintage mic
    out = np.tanh(out / (np.max(np.abs(out)) + 1e-9) * 1.6)
    return out / np.max(np.abs(out))


def announce(n_samples):
    out = np.zeros(n_samples)
    for t, line in INTRO:
        x = tts(line, ANNOUNCER, 150)
        x = signal.sosfilt(signal.butter(2, [180, 5500], 'band', fs=SR, output='sos'), x)  # showroom PA
        x = np.tanh(x / (np.max(np.abs(x)) + 1e-9) * 1.4)
        i = int(t * SR)
        out[i:i + len(x)] += x[: max(0, n_samples - i)]
    return out / (np.max(np.abs(out)) + 1e-9)
