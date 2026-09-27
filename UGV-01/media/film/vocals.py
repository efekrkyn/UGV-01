"""Turkish vocals for the UGV-01 film (sung version, `music.py --vocal`; pyworld via uv, see make_film.sh).

A woman's voice sings the original Turkish lyrics in README.md. The voice is macOS `say` Yelda: every syllable is spoken
on its own and analysed with the WORLD vocoder, then laid on its note the way a singer does it: consonants keep their
natural length and come just before the beat, the vowel stretches to fill the note (its edges untouched), the pitch
follows the melody with a small scoop and overshoot and a late vibrato on long notes. The whole track is resynthesised
as one continuous phrase, so the voice keeps its own timbre instead of sounding vocoded.
"""
from functools import lru_cache
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
import pyworld as pw
from scipy import signal
from scipy.io import wavfile

SR = 48000  # film audio
FS = 22050  # Yelda's native rate; WORLD runs here
HOP = 0.005  # WORLD frame period, s
VOICE = 'Yelda'
F0_FLOOR = 80
FFT = pw.get_cheaptrick_fft_size(FS, F0_FLOOR)
FREQS = np.linspace(0, FS / 2, FFT // 2 + 1)
BAND = (FREQS > 250) & (FREQS < 3500)
MAX_CONS = int(0.15 / HOP)  # longest consonant run kept at natural speed, frames

# (bar, beat, 'hyphenated syllables', notes): one (midi, beats) per syllable, a list of them for a melisma,
# (None, beats) for a rest. Chords per bar are music.CHART; verses in F, the chorus in G after the pivot.
VERSE1 = [
    (4, 0, 'dört te-ker-le a-ğır a-ğır ge-lir',
     [(60, 1), (62, .667), (65, .333), (69, 1), (67, .667), (65, .333), (69, .667), (65, .333), (62, .667), (65, 2)]),
    (6, 0, 'her dö-nü-şü-nü tek tek bi-lir',
     [(62, .667), (65, .333), (67, .667), (65, .333), (62, 1), (64, .667), (65, .333), (67, 1), (64, 2.5)]),
    (8, 0, 'i-ki cam göz-le o-da-yı o-kur',
     [(64, .667), (67, .333), (69, 1), (72, .667), (69, .333), (67, .667), (66, .333), (69, .667), (72, .333), (69, 2.5)]),
    (10, 0, 'kü-pü sen-den ön-ce bu-lur',
     [(67, .667), (65, .333), (62, .667), (64, .333), (67, 1), (64, .667), (65, .333), (69, 3)]),
]
VERSE2 = [
    (12, 0, 'dok-san al-tı par-ça faz-la-sı yok',
     [(60, .667), (62, .333), (65, .667), (69, .333), (72, .667), (69, 1.333), (69, .667), (67, .333), (65, 1), (62, 1.75)]),
    (14, 0, 'her a-çı-ya ba-kıl-mış ek-si-ği yok',
     [(62, .667), (65, .333), (67, .667), (65, .333), (62, .667), (65, .333), (67, 1), (70, .667), (67, .333), (64, 1),
      (60, 1.75)]),
    (16, 0, 'ko-lu ye-di yol-dan u-za-nır',
     [(64, .667), (67, .333), (69, .667), (72, .333), (72, 1), (69, 1), (66, .667), (69, .333), (72, 2.5)]),
    (18, 0, 'bir kez ol-sun çarp-maz sa-kı-nır',
     [(70, .667), (69, .333), (67, .667), (65, .333), (64, .667), (67, 1.333), (69, .667), (67, .333), (65, 2.5)]),
]
BRIDGE = [  # safety section; the last "de" is held over the D7 pivot into the key change
    (32, 0, 'a-ma dur de taş gi-bi du-rur',
     [(60, .667), (62, .333), (65, 1), (69, 2), (72, 1), (69, .667), (69, .333), (69, .667), (69, 1.333)]),
    (34, 0, 'çün-kü fren dos-tum se-nin e-lin-de',
     [(62, .667), (65, .333), (67, 1), (70, .667), (69, 1.333), (None, 1), (64, .667), (67, .333), (70, 1), (67, 1),
      [(67, .667), (69, 6.333)]]),
]
CHORUS = [  # shout chorus, G major
    (38, 0, 'kü-çük a-ma cid-di iş', [(71, .667), (74, 1.333), (71, .667), (69, 1.333), (71, .667), (67, .333), (64, 2.5)]),
    (40, 0, 'te-mel-den sağ-lam iş', [(69, .667), (72, .333), (76, 1), (74, .667), (72, 1.333), (69, 3)]),
    (42, 0, 'her me-sa-jı im-za-lı', [(69, .667), (71, .333), (74, .667), (71, .333), (69, .667), (71, .333), (66, .9)]),
    (43, 0, 'her a-dı-mı he-sap-lı', [(68, .667), (71, .333), (74, .667), (71, .333), (68, .667), (71, .333), (64, 1)]),
    (44, 0, 'a-ğır-lı-ğı al-çak-ta sö-zü-nün e-ri o',
     [(69, .667), (72, .333), (76, .667), (74, .333), (72, .667), (69, .333), (66, 1), (67, .667), (69, .333), (71, .667),
      (72, .333), (74, .667), (71, 1.333)]),
]
CODA = [  # after the button, soft over the strings
    (46, 1, 'kü-çük ro-bot bü-yük iş', [(67, .5), (71, .5), (74, .5), (71, 1.5), (None, .5), (69, .5), (71, .5), (67, 3)]),
]
SUNG = VERSE1 + VERSE2 + BRIDGE + CHORUS + CODA
LOUD = (38, 46)  # bars sung out (the shout chorus)
INTRO = [(0.35, 'Hanımlar, beyler...'), (2.05, 'karşınızda: küçük robot!')]


def tts(text, rate=140):
    with tempfile.TemporaryDirectory() as tmp:
        aiff, wav = Path(tmp) / 'w.aiff', Path(tmp) / 'w.wav'
        subprocess.run(['say', '-v', VOICE, '-r', str(rate), '-o', str(aiff), text], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-ac', '1', '-ar', str(FS), str(wav)], check=True)
        _, x = wavfile.read(wav)
    x = x.astype(np.float64) / 32768
    loud = np.flatnonzero(np.abs(x) > 0.02 * np.max(np.abs(x)))
    return x[max(loud[0] - 120, 0): loud[-1] + 120] if len(loud) else x


@lru_cache(maxsize=None)
def syllable(text):
    """WORLD parameters of one spoken syllable, its vowel span in frames, normalised so every vowel peaks alike."""
    x = tts(text.lstrip('ğ') or text)  # a syllable never starts with ğ when spoken: "a-ğır" is "a-ır"
    f0, t = pw.harvest(x, FS, f0_floor=F0_FLOOR, f0_ceil=600, frame_period=HOP * 1000)
    sp = pw.cheaptrick(x, f0, t, FS, fft_size=FFT)
    ap = pw.d4c(x, f0, t, FS, fft_size=FFT)
    e = 10 * np.log10(sp[:, BAND].sum(1) + 1e-16)
    peak = e[f0 > 0].max() if np.any(f0 > 0) else e.max()  # the vowel's level, not a loud ç or ş
    vowel = np.flatnonzero((f0 > 0) & (e > peak - 6))
    v0, v1 = (vowel[0], vowel[-1] + 1) if len(vowel) else (0, len(f0))
    return f0, sp / 10 ** (peak / 10), ap, v0, v1


def events(at, beat):
    """Every sung syllable: (text, start s, end s, bar, [(midi, s0, s1), ...])."""
    out = []
    for bar, b, text, line in SUNG:
        sylls, t, k = re.split(r'[ -]+', text), at(bar, b), 0
        for item in line:
            if item[0] is None:
                t += item[1] * beat
                continue
            notes, t0 = [], t
            for m, beats in item if isinstance(item, list) else [item]:
                notes.append((m, t, t + beats * beat))
                t += beats * beat
            out.append((sylls[k], t0, t, bar, notes))
            k += 1
        assert k == len(sylls), text
    return out


def pitch_track(evs, n):
    """Sung pitch in cents from A4 per frame: held through rests, a small scoop into each phrase, a quick glide with a
    little overshoot between notes, late vibrato on long notes and a slow wander of a few cents."""
    target, vib = np.full(n, np.nan), np.zeros(n)
    for *_, notes in evs:
        for m, s0, s1 in notes:
            j0, j1 = int(round(s0 / HOP)), int(round(s1 / HOP))
            target[j0:j1] = (m - 69) * 100
            if s1 - s0 > 0.45:
                tt = np.arange(j1 - j0) * HOP
                vib[j0:j1] = 30 * np.sin(2 * np.pi * 5.4 * tt) * np.clip((tt - 0.2) / 0.3, 0, 1)
    sung = ~np.isnan(target)
    starts = np.flatnonzero(sung & ~np.roll(sung, 1))
    for j in starts:  # the rest before a phrase sits a semitone and a half under its first note
        target[max(j - 30, 0):j][np.isnan(target[max(j - 30, 0):j])] = target[j] - 150
    idx = np.where(~np.isnan(target), np.arange(n), 0)
    np.maximum.accumulate(idx, out=idx)
    held = target[idx]
    held[:starts[0]] = target[starts[0]]
    w, z = 2 * np.pi * 9, 0.55
    b, a, _ = signal.cont2discrete(([w * w], [1, 2 * z * w, w * w]), HOP, method='bilinear')
    glide = signal.lfilter(b.ravel(), a, held, zi=signal.lfilter_zi(b.ravel(), a) * held[0])[0]
    wander = signal.sosfiltfilt(signal.butter(2, 2, 'low', fs=1 / HOP, output='sos'),
                                np.random.default_rng(7).standard_normal(n)) * 25
    return glide + vib + wander, vib


def sing(n_samples, at, beat):
    """Mono vocal track, n_samples at 48 kHz. `at(bar, beat)` gives seconds."""
    evs = events(at, beat)
    n = int(n_samples / SR / HOP) + 1
    cents, vib = pitch_track(evs, n)
    f0 = np.zeros(n)
    logsp = np.full((n, FFT // 2 + 1), -40.0)
    ap = np.ones((n, FFT // 2 + 1))
    gain = np.zeros(n)
    legato = [i + 1 < len(evs) and evs[i + 1][1] - evs[i][2] < 0.05 for i in range(len(evs))]
    # the consonant before a vowel comes ahead of the beat, shortened on fast notes so the note before keeps its vowel
    pre = [min(syllable(e[0])[3], MAX_CONS, int(0.35 * (evs[i - 1][2] - evs[i - 1][1]) / HOP) if i and legato[i - 1]
               else MAX_CONS) for i, e in enumerate(evs)]
    for i, (text, t0, t1, bar, notes) in enumerate(evs):
        sf0, ssp, sap, v0, v1 = syllable(text)
        start = int(round(t0 / HOP)) - pre[i]
        end = int(round(evs[i + 1][1] / HOP)) - pre[i + 1] if legato[i] else int(round((t1 - 0.06) / HOP))
        span, total = end - start, len(sf0)
        coda = min(total - v1, MAX_CONS, max(span - pre[i], 0) // 3)
        edge = min(6, (v1 - v0) // 3)
        vend = span - coda
        out_knots = [0, pre[i], pre[i] + edge, vend - edge, vend, span]
        src_knots = [0, v0, v0 + edge, v1 - edge, v1, total]
        if np.any(np.diff(out_knots) < 0) or vend - pre[i] < 2 * edge + 2:  # too short to hold: speak it at that speed
            out_knots, src_knots = [0, span], [0, total]
        src = np.interp(np.arange(span), out_knots, src_knots)
        lo = np.clip(np.floor(src).astype(int), 0, total - 1)
        hi = np.minimum(lo + 1, total - 1)
        w = (src - lo)[:, None]
        j = np.arange(start, end)
        ok = (j >= 0) & (j < n)
        j, lo, hi, w = j[ok], lo[ok], hi[ok], w[ok]
        logsp[j] = (1 - w) * np.log(ssp[lo] + 1e-16) + w * np.log(ssp[hi] + 1e-16)
        ap[j] = (1 - w) * sap[lo] + w * sap[hi]
        voiced = sf0[np.rint(src[ok]).astype(int).clip(0, total - 1)] > 0
        f0[j] = np.where(voiced, 440 * 2 ** (cents[j] / 1200), 0)
        tt = j * HOP - t0
        dur = t1 - t0
        env = 1 - 0.12 * np.clip(tt / max(dur, 0.3), 0, 1)  # long notes relax a little
        env *= 1 + 0.004 * vib[j]  # tremolo that rides with the vibrato
        if not legato[i]:
            env *= np.clip((end * HOP - j * HOP) / 0.04, 0, 1)  # release at the end of a phrase
        gain[j] = env * (1.3 if LOUD[0] <= bar < LOUD[1] else 1.0)
    voiced = f0 > 0
    alpha = np.where(voiced, (np.maximum(f0, 1) / 165) ** 0.07, 1)  # formants rise a touch with the note, as sung
    for k in np.flatnonzero(voiced & (np.abs(alpha - 1) > 0.005)):
        logsp[k] = np.interp(FREQS / alpha[k], FREQS, logsp[k])
    logsp = signal.sosfiltfilt(signal.butter(2, 40, 'low', fs=1 / HOP, output='sos'), logsp, axis=0)  # smooth joins
    sp = np.exp(logsp) * gain[:, None] ** 2 + 1e-16
    breath = 0.18 * np.clip((FREQS - 2500) / 4000, 0, 1)  # a little air on top
    ap = np.clip(1 - (1 - ap) * (1 - breath), 0, 1)
    y = pw.synthesize(f0, np.ascontiguousarray(sp), np.ascontiguousarray(ap), FS, HOP * 1000)
    y = signal.resample_poly(y, 320, 147)  # 22.05 -> 48 kHz
    y = signal.sosfilt(signal.butter(2, [90, 11000], 'band', fs=SR, output='sos'), y)
    y = np.pad(y, (0, max(0, n_samples - len(y))))[:n_samples]
    return y / (np.max(np.abs(y)) + 1e-9)


def announce(n_samples):
    out = np.zeros(n_samples)
    for t, line in INTRO:
        x = signal.resample_poly(tts(line, 150), 320, 147)
        x = signal.sosfilt(signal.butter(2, [180, 5500], 'band', fs=SR, output='sos'), x)  # showroom PA
        x = np.tanh(x / (np.max(np.abs(x)) + 1e-9) * 1.4)
        i = int(t * SR)
        out[i:i + len(x)] += x[: max(0, n_samples - i)]
    return out / (np.max(np.abs(out)) + 1e-9)
