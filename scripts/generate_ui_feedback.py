"""Generate the original, low-volume UI feedback sprite used by simple.html."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
DURATION = 0.48
TARGET_PEAK = 0.28
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "ui-feedback.wav"


def add_soft_tap(
    samples: list[float],
    *,
    start: float,
    frequency: float,
    amplitude: float,
    decay: float,
    seed: int,
) -> None:
    """Add a damped, wooden-feeling tap without a sustained electronic tone."""
    rng = random.Random(seed)
    start_frame = round(start * SAMPLE_RATE)
    tap_frames = round(0.09 * SAMPLE_RATE)
    body_phase = 0.0
    wood_phase = 0.0
    dull_noise = 0.0

    for frame in range(tap_frames):
        t = frame / SAMPLE_RATE
        attack = min(1.0, t / 0.0018)
        body_envelope = math.exp(-t / decay)
        wood_envelope = math.exp(-t / 0.011)
        noise_envelope = math.exp(-t / 0.0065)

        # A real impact relaxes slightly in pitch; the change is intentionally tiny.
        relaxed_frequency = frequency * (1.0 + 0.028 * math.exp(-t / 0.012))
        body_phase += 2.0 * math.pi * relaxed_frequency / SAMPLE_RATE
        wood_phase += 2.0 * math.pi * (frequency * 2.67) / SAMPLE_RATE

        white_noise = rng.uniform(-1.0, 1.0)
        dull_noise += 0.14 * (white_noise - dull_noise)
        value = amplitude * attack * (
            0.82 * math.sin(body_phase) * body_envelope
            + 0.13 * math.sin(wood_phase + 0.35) * wood_envelope
            + 0.05 * dull_noise * noise_envelope
        )

        target = start_frame + frame
        if target < len(samples):
            samples[target] += value


def build_sprite() -> None:
    samples = [0.0] * round(DURATION * SAMPLE_RATE)

    # 不会：单个较低、较钝的触碰声。
    add_soft_tap(
        samples,
        start=0.012,
        frequency=142.0,
        amplitude=0.23,
        decay=0.034,
        seed=11,
    )

    # 模糊：两个很轻的触碰，靠节奏而不是滑频来表达“不确定”。
    add_soft_tap(
        samples,
        start=0.132,
        frequency=176.0,
        amplitude=0.145,
        decay=0.025,
        seed=21,
    )
    add_soft_tap(
        samples,
        start=0.188,
        frequency=184.0,
        amplitude=0.12,
        decay=0.023,
        seed=22,
    )

    # 会了：三次逐渐变轻的木质触碰，避免明亮的电子和弦。
    add_soft_tap(
        samples,
        start=0.292,
        frequency=178.0,
        amplitude=0.14,
        decay=0.026,
        seed=31,
    )
    add_soft_tap(
        samples,
        start=0.337,
        frequency=218.0,
        amplitude=0.105,
        decay=0.023,
        seed=32,
    )
    add_soft_tap(
        samples,
        start=0.382,
        frequency=254.0,
        amplitude=0.075,
        decay=0.020,
        seed=33,
    )

    peak = max(abs(sample) for sample in samples)
    if peak > TARGET_PEAK:
        scale = TARGET_PEAK / peak
        samples = [sample * scale for sample in samples]

    pcm = b"".join(
        struct.pack("<h", round(max(-1.0, min(1.0, sample)) * 32767))
        for sample in samples
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(SAMPLE_RATE)
        sound.writeframes(pcm)


if __name__ == "__main__":
    build_sprite()
