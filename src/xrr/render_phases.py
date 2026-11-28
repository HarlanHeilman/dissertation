"""Render a module's PHASES as separate clips sharing boundary frames, plus the full clip.
Usage: python3 render_phases.py out_dir g12 g13"""
import sys, os, subprocess, importlib
from style import FPS
out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def encode(name, frames_fn, n, size):
    mkv = f"{out}/{name}.mkv"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0",
                          "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-", "-c:v", "ffv1", mkv],
                         stdin=subprocess.PIPE)
    for i in range(n):
        s = frames_fn(i)
        s.flush()
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close(); assert p.wait() == 0
    pal = f"{out}/{name}.pal.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mkv, "-vf", "palettegen=max_colors=256:stats_mode=full", pal], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mkv, "-i", pal, "-lavfi", "paletteuse=dither=sierra2_4a",
                    "-loop", "-1", f"{out}/{name}.gif"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mkv, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-preset", "veryfast", "-movflags", "+faststart", f"{out}/{name}.mp4"], check=True)
    os.remove(pal)
    print(name, n, "frames")


mods = [importlib.import_module(m) for m in sys.argv[2:]]
for mod in mods:
    for name, a, b in mod.PHASES:
        n = int(round((b - a) * FPS)) + 1          # include both ends
        encode(f"xrr-{name}", lambda i, a=a, mod=mod: mod.frame(a + i / FPS), n, mod.SIZE)

# full sequence: every module end to end (boundary frame shared once)
seq = []
for k, mod in enumerate(mods):
    n = int(round(mod.DUR * FPS)) + 1
    seq += [(mod, i / FPS) for i in range(1 if k else 0, n)]
encode("xrr-full", lambda i: seq[i][0].frame(seq[i][1]), len(seq), mods[0].SIZE)
