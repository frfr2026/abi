#!/usr/bin/env python3
"""ABI NEXUS — procedural synthesis of ambiances & SFX (MP3, 192kbps).
All audio generated with numpy/scipy + lameenc. Deterministic (seeded)."""
import os
import numpy as np
from scipy import signal
import lameenc

SR = 44100
OUT = "/home/user/audio"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def tt(dur):
    return np.arange(max(1, int(dur * SR))) / SR


def bp(x, lo, hi, order=4):
    b, a = signal.butter(order, [max(lo, 20) / (SR / 2), min(hi, 20000) / (SR / 2)], btype="band")
    return signal.filtfilt(b, a, x)


def lp(x, f, order=4):
    b, a = signal.butter(order, min(f, 20000) / (SR / 2), "low")
    return signal.filtfilt(b, a, x)


def hp(x, f, order=4):
    b, a = signal.butter(order, max(f, 10) / (SR / 2), "high")
    return signal.filtfilt(b, a, x)


def add(buf, sig, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += sig[:n] * gain


def norm(x, peak=0.89):
    m = np.max(np.abs(x))
    return x if m == 0 else x * (peak / m)


def saw(freq, dur):
    return signal.sawtooth(2 * np.pi * freq * tt(dur))


def sine(freq, dur):
    return np.sin(2 * np.pi * freq * tt(dur))


def pluck(freq, dur, bright=0.6):
    t = tt(dur)
    env = np.exp(-t * 8)
    x = np.sin(2 * np.pi * freq * t) + bright * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 16)
    return x * env


def noise(dur):
    return rng.standard_normal(max(1, int(dur * SR)))


def kick(dur=0.5, f0=140, f1=40):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7)


def taiko(dur=0.9, f0=110, f1=55):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 10)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 4.5)
    hit = bp(noise(dur), 300, 3000) * np.exp(-t * 40) * 0.35
    return body + hit


def hat(dur=0.08):
    t = tt(dur)
    return bp(noise(dur), 6000, 14000) * np.exp(-t * 60)


def thump(dur=0.6, f=60):
    t = tt(dur)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 9)


def reverb(x, decay=1.6, mix=0.35, seed=1):
    r = np.random.default_rng(seed)
    n = int(decay * SR)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 5, n))
    ir = lp(ir, 5000)
    ir /= np.max(np.abs(ir)) or 1
    wet = signal.fftconvolve(x, ir)[:len(x)]
    wet /= np.max(np.abs(wet)) or 1
    return (1 - mix) * x + mix * wet * (np.max(np.abs(x)) or 1)


def stereoize(x, width_ms=14, gain_r=0.92):
    d = int(width_ms / 1000 * SR)
    l = x
    r = np.concatenate([np.zeros(d), x[:-d]]) if 0 < d < len(x) else x.copy()
    return np.stack([l, gain_r * r], axis=1)


def save(name, x, sr=SR):
    x = norm(np.asarray(x))
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    enc = lameenc.Encoder()
    enc.set_bit_rate(192)
    enc.set_in_sample_rate(sr)
    enc.set_channels(2)
    enc.set_quality(2)
    data = enc.encode(pcm.tobytes()) + enc.flush()
    path = os.path.join(OUT, name)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  {name}: {len(data)//1024} KB")


# ── CHORDS ──────────────────────────────────────────────────
CH = {
    "Am": [110.0, 164.81, 220.0, 261.63],
    "F":  [87.31, 174.61, 220.0, 261.63],
    "C":  [130.81, 196.0, 261.63, 329.63],
    "G":  [98.0, 196.0, 246.94, 293.66],
    "Dm": [73.42, 146.83, 220.0, 293.66],
    "Em": [82.41, 164.81, 246.94, 329.63],
}


def pad_chord(freqs, dur, cutoff=1800, gain=0.5, attack=1.2, release=1.5):
    n = int(dur * SR)
    pad = np.zeros(n)
    for f in freqs:
        for dt in (0.997, 1.0, 1.004):
            s = saw(f * dt, dur)
            m = min(len(s), n)
            pad[:m] += s[:m]
    pad /= len(freqs) * 3
    env = np.ones(n)
    na = int(attack * SR)
    nr = int(release * SR)
    if na > 0:
        env[:na] = np.linspace(0, 1, na) ** 0.8
    if nr > 0:
        env[-nr:] *= np.linspace(1, 0, nr) ** 0.8
    return lp(pad, cutoff) * env * gain


# ── AMBIANCE : MENU (épique orchestral + électronique) ──────
def ambiance_menu(dur=120):
    buf = np.zeros(int(dur * SR))
    chord_len = 8.0
    prog = ["Am", "F", "C", "G", "Am", "Dm", "G", "Em"]
    i = 0
    t0 = 0.0
    while t0 < dur:
        ch = prog[i % len(prog)]
        freqs = CH[ch]
        add(buf, pad_chord(freqs, chord_len + 1.5, 1900, 0.55), t0)
        root = freqs[0] / 2
        for off in np.arange(0, chord_len, 2.0):
            add(buf, sine(root, 2.0) * np.exp(-tt(2.0) * 1.2), t0 + off, 0.40)
        for off in np.arange(0, chord_len, 2.0):
            g = 1.0 if off == 0 else 0.62
            add(buf, taiko(), t0 + off, 0.72 * g)
        for off in np.arange(0.5, chord_len, 1.0):
            add(buf, hat(), t0 + off, 0.10)
        add(buf, pluck(freqs[2] * 2, 1.6), t0 + 1.0, 0.16)
        add(buf, pluck(freqs[3] * 2, 1.3), t0 + 5.2, 0.12)
        t0 += chord_len
        i += 1
    buf = reverb(buf, 2.2, 0.38, seed=3)
    return stereoize(buf)


# ── AMBIANCE : TACTICAL (tension tactique, basses) ──────────
def ambiance_tactical(dur=120):
    buf = np.zeros(int(dur * SR))
    t = tt(dur)
    # drone bas
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 55.4 * t)
             + 0.4 * np.sin(2 * np.pi * 110 * t))
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    add(buf, drone * lfo, 0, 0.16)
    # pad cluster mi mineur
    pad = np.zeros(int(dur * SR))
    for f in (164.81, 196.0, 246.94, 329.63):
        s = saw(f * 1.001, dur)
        m = min(len(s), len(pad))
        pad[:m] += s[:m]
    pad = lp(pad, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t)) * 0.09
    add(buf, pad, 0)
    # battement cardiaque
    off = 0.0
    while off < dur:
        add(buf, thump(0.5, 55), off, 0.30)
        add(buf, thump(0.35, 50), off + 0.28, 0.16)
        off += 1.3
    # stings électroniques
    st = 5.0
    penta = [440.0, 523.25, 587.33, 659.25, 783.99]
    while st < dur - 4:
        f = penta[int(rng.integers(0, len(penta)))]
        for k in range(3):
            add(buf, pluck(f * (1 + 0.02 * k), 0.6), st + k * 0.18, 0.08)
        st += float(rng.uniform(7, 11))
    # craquement lointain (tir sourd)
    cr = 12.0
    while cr < dur - 3:
        c = bp(noise(0.35), 700, 4200) * np.exp(-tt(0.35) * 18)
        add(buf, c, cr, 0.10)
        cr += float(rng.uniform(14, 22))
    buf = reverb(buf, 1.8, 0.30, seed=5)
    return stereoize(buf, 18)


# ── AMBIANCE : ZOMBIE (horreur biohazard) ───────────────────
def ambiance_zombie(dur=120):
    buf = np.zeros(int(dur * SR))
    t = tt(dur)
    # ronflement grave (brown noise)
    brown = lp(noise(dur), 110)
    brown = brown / (np.max(np.abs(brown)) or 1)
    add(buf, brown * (0.4 + 0.3 * np.sin(2 * np.pi * 0.04 * t)), 0, 0.30)
    # grappe dissonante
    cluster = np.zeros(int(dur * SR))
    for f in (98.0, 103.8, 146.83, 147.95):
        s = saw(f, dur)
        m = min(len(s), len(cluster))
        cluster[:m] += s[:m]
    cluster = lp(cluster, 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.017 * t + 1.0)) * 0.10
    add(buf, cluster, 0)
    # grognements
    gr = 4.0
    while gr < dur - 3:
        d = float(rng.uniform(1.4, 2.4))
        g = bp(noise(d), 170, 720)
        env = np.sin(np.linspace(0, np.pi, len(g))) ** 1.3
        wob = 1 + 0.4 * np.sin(2 * np.pi * rng.uniform(4, 7) * tt(d))
        g = np.tanh(g * wob * env * 3) * 0.16
        add(buf, g, gr)
        gr += float(rng.uniform(6, 10))
    # cris métalliques aigus
    sc = 9.0
    while sc < dur - 3:
        d = 1.0
        f = float(rng.uniform(3000, 4200))
        s = np.sin(2 * np.pi * f * tt(d) + 4 * np.sin(2 * np.pi * 8 * tt(d)))
        add(buf, s * np.exp(-tt(d) * 5), sc, 0.030)
        sc += float(rng.uniform(15, 25))
    # impacts sourds irréguliers
    th = 7.0
    while th < dur - 2:
        add(buf, taiko(1.2, 90, 42), th, 0.35)
        th += float(rng.uniform(9, 15))
    buf = reverb(buf, 2.4, 0.42, seed=9)
    return stereoize(buf, 22, 0.88)


# ── AMBIANCE : DARK ZONE (tension extrême, métal) ───────────
def ambiance_darkzone(dur=120):
    buf = np.zeros(int(dur * SR))
    # souffles profonds
    rm = 0.0
    while rm < dur - 6:
        d = 8.0
        r = lp(noise(d), 60)
        r = r / (np.max(np.abs(r)) or 1)
        env = np.sin(np.linspace(0, np.pi, len(r))) ** 2
        add(buf, r * env, rm, 0.35)
        rm += float(rng.uniform(14, 20))
    # pings métalliques
    pg = 3.0
    while pg < dur - 4:
        d = 2.5
        s = np.zeros(int(d * SR))
        for f in (1180.0, 1794.0, 2631.0, 3517.0):
            s[: int(d * SR)] += sine(f, d)[: int(d * SR)] * float(rng.uniform(0.5, 1.0))
        t = tt(d)
        s *= np.exp(-t * 3.2)
        add(s, bp(noise(0.05), 2000, 7000) * np.exp(-tt(0.05) * 80), 0, 2.0)
        add(buf, s, pg, 0.10)
        pg += float(rng.uniform(5, 10))
    # griffures métalliques
    sc = 11.0
    while sc < dur - 3:
        d = 1.2
        n = bp(noise(d), 1400, 3600)
        sweep = np.sin(np.linspace(0, 1, len(n)) * np.pi)
        add(buf, n * sweep, sc, 0.05)
        sc += float(rng.uniform(12, 20))
    buf = reverb(buf, 3.0, 0.5, seed=11)
    return stereoize(buf, 25, 0.85)


# ── SFX ─────────────────────────────────────────────────────
def sfx_hover():
    d = 0.25
    t = tt(d)
    click = bp(noise(d), 3000, 7000) * np.exp(-t * 130)
    blip = np.sin(2 * np.pi * 1300 * t) * np.exp(-t * 60)
    x = click * 0.8 + blip * 0.5
    return x * 0.7


def sfx_click():
    d = 0.4
    t = tt(d)
    c1 = bp(noise(0.06), 1500, 5000) * np.exp(-tt(0.06) * 120)
    x = np.zeros(int(d * SR))
    add(x, c1, 0.0, 0.9)
    add(x, c1 * 0.7, 0.06, 0.7)
    low = np.sin(2 * np.pi * 170 * t) * np.exp(-t * 30)
    add(x, low, 0.0, 0.5)
    return x


def sfx_transition():
    d = 0.8
    n = noise(d)
    # balayage fréquentiel (chirp filtré)
    out = np.zeros(len(n))
    seg = 8
    step = len(n) // seg
    for i in range(seg):
        lo = 300 + i * 700
        hi = lo + 1800
        chunk = bp(n[i * step:(i + 1) * step], lo, hi) if i < seg - 1 else bp(n[i * step:], lo, hi)
        out[i * step:i * step + len(chunk)] = chunk
    env = np.sin(np.linspace(0, np.pi, len(out))) ** 1.5
    return out * env * 1.1


def sfx_weapon_equip():
    d = 1.4
    x = np.zeros(int(d * SR))

    def clack(freq, gain, dur=0.16):
        t = tt(dur)
        c = bp(noise(dur), freq * 0.5, freq * 2.2) * np.exp(-t * 90)
        r = np.sin(2 * np.pi * freq * t) * np.exp(-t * 70)
        return (c * 0.9 + r * 0.6) * gain

    add(x, clack(2200, 0.9), 0.00)
    # glissement de culasse
    slide = bp(noise(0.28), 800, 3800) * np.sin(np.linspace(0, np.pi, int(0.28 * SR))) ** 2
    add(x, slide, 0.16, 0.7)
    add(x, clack(1600, 0.8), 0.46)
    # insertion chargeur
    add(x, clack(1100, 0.7), 0.72)
    add(x, thump(0.3, 90), 0.74, 0.5)
    # relâchement du verre
    add(x, clack(3000, 0.6, 0.12), 1.00)
    return x


def sfx_extraction():
    d = 3.0
    t = tt(d)
    # rotor hélico (bruit modulé)
    carrier = lp(noise(d), 1400)
    am = np.abs(np.sin(np.pi * 13.5 * t)) ** 3
    ramp = np.minimum(1.0, t / 1.2) * np.exp(-np.maximum(0, t - 2.2) * 2)
    rotor = carrier * am * ramp
    # nappe chaleureuse (soulagement)
    chord = (np.sin(2 * np.pi * 261.63 * t) + np.sin(2 * np.pi * 329.63 * t)
             + np.sin(2 * np.pi * 392.0 * t) + 0.6 * np.sin(2 * np.pi * 523.25 * t))
    swell = np.minimum(1.0, np.maximum(0, (t - 0.4)) / 1.0) * np.exp(-np.maximum(0, t - 2.0) * 1.5)
    x = rotor * 0.8 + chord * swell * 0.10
    return reverb(x, 1.2, 0.25, seed=21)


def sfx_zombie_alert():
    d = 1.8
    t = tt(d)
    # alarme dissonante
    alarm = (signal.sawtooth(2 * np.pi * 660 * t) + signal.sawtooth(2 * np.pi * 698.4 * t)) * 0.5
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 12 * t)
    env = np.minimum(1, t * 12) * np.exp(-np.maximum(0, t - 1.1) * 6)
    alarm = lp(alarm * trem * env, 3500)
    # grognement de rage
    g = bp(noise(d), 140, 520)
    g = np.tanh(g * 3.5) * (np.minimum(1, t * 3) * np.exp(-np.maximum(0, t - 1.4) * 4))
    x = alarm * 0.55 + g * 0.40
    add(x, thump(0.5, 50), 0, 0.5)
    return reverb(x, 1.0, 0.3, seed=31)


# ── GÉNÉRATION ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Génération des ambiances (120 s chacune)...")
    save("ambiance-menu.mp3", ambiance_menu(120))
    save("ambiance-tactical.mp3", ambiance_tactical(120))
    save("ambiance-zombie.mp3", ambiance_zombie(120))
    save("ambiance-dark-zone.mp3", ambiance_darkzone(120))
    print("Génération des SFX...")
    save("sfx-hover.mp3", sfx_hover())
    save("sfx-click.mp3", sfx_click())
    save("sfx-transition.mp3", sfx_transition())
    save("sfx-weapon-equip.mp3", sfx_weapon_equip())
    save("sfx-extraction.mp3", sfx_extraction())
    save("sfx-zombie-alert.mp3", sfx_zombie_alert())
    print("Terminé — 10 fichiers MP3 dans", OUT)
