import sys, importlib, subprocess, os, time
from style import W, H, FPS
name = sys.argv[1]; out = sys.argv[2]
mod = importlib.import_module(name)
n = int(round(mod.DUR * FPS))
W, H = getattr(mod, "SIZE", (W, H))
os.makedirs(out, exist_ok=True)
master = f"{out}/{name}.tmp.mkv"
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "ffv1", master], stdin=subprocess.PIPE)
t0 = time.time()
for i in range(n):
    s = mod.frame(i / FPS)
    s.flush()
    p.stdin.write(bytes(s.get_data()))
p.stdin.close(); assert p.wait() == 0
os.replace(master, f"{out}/{name}.mkv")
print(name, n, "frames", round(time.time() - t0, 1), "s")
