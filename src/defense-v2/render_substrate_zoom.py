"""Regenerate the FIG4 panel (c) growth strip zoomed onto the substrate, with the lying contact islands
recoloured (PATCH_STYLE = "color", red palette) instead of the red glow, using the FIG4 notebook settings
and the published graded fit (bookended_multienergy_logY_polish_open_sliced). Drawn with depth horizontal
(vacuum left, Si right) at the zoom scale, then rotated so the substrate sits at the bottom."""
import sys, importlib
from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
from PIL import Image
MS = Path("/home/claude/refl/notebooks/manuscript"); sys.path.insert(0, str(MS)); sys.path.insert(0, "/home/claude/refl/src")
from legacy_pyref.models import configure_refloxide_fitting
from legacy_pyref.graded_objective import extract_graded_fit_context, load_bookended_multienergy_logY_polish
import json
configure_refloxide_fitting()
gp = load_bookended_multienergy_logY_polish(Path("/home/claude/refl/@models/fitting_results/bookended_multienergy_logY_polish_open_sliced/fit.pkl"))
film = extract_graded_fit_context(gp.at(283.7)).film
nb = json.load(open(MS / "FIG4.ipynb"))
cell2 = "".join(nb["cells"][[i for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"][2]]["source"])
ns = {}
exec("import numpy as np\nfrom scipy.special import erf\n" + cell2[:cell2.find("def slab_film_profiles")], ns)
Z_G, RHO_SHARP, _ = ns["nevot_croce_density"](film)
ALPHA_ROUGH = ns["nevot_croce_orientation"](film, Z_G, RHO_SHARP)
import fig4_panel_b_growth as F
F.SUBSTRATE_MODE = "off"; F.SUB_CLEAR = 1; F.SEED = 10; F.PACKING = "crystal"
F.CLASH_A = 1.8; F.SUB_ROUGH_A = 2.7; F.SURFACE_VACANCIES = True; F.SETTLE_ZONE_TAU = 10.0
F.FILM_DENSE = False; F.DENSITY_CORRECT = True; F.CONTACT_KEEP_MIN = 0.55
F.PATCH_SEED = 2; F.CONTACT_PATCH_PERIODS_A = (22.0, 33.0, 51.0); F.PATCH_GLOW = True
F.PATCH_STYLE = "color"; F.PATCH_PALETTE = "red"; F.CONTACT_PATCHES = True; F.CONTACT_TILT_DEG = 28.0
F.PATCH_SINK_A = 3.0; F.DRAW_BEHIND = True; F.BEHIND_GREY = "0.70"; F.BEHIND_ALPHA = 0.25
F.L_MOL = 14.95; F.LAT_FRAC = 0.955
info = F.configure_packing(film, z_left=-6.0, z_g=Z_G, rho_sharp=RHO_SHARP, alpha_g=ALPHA_ROUGH, slab_thick=14.37,
                           highlight_fn=lambda ax, *, halo=True: None, xyz_path=MS / "tpznpc_0m.xyz")
L = info["total"]
def _ppa(ax):
    fig_ = ax.get_figure(); w_in = ax.get_position().width * fig_.get_size_inches()[0]
    x0, x1 = ax.get_xlim(); return float(w_in * 72.0 / (x1 - x0))
F._points_per_angstrom = _ppa   # widths follow the zoomed axes, not the full-film span
HTOP, HBOT = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0, -6.0      # heights above the oxide, Angstrom
YH = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0                      # lateral half width, Angstrom
span = HTOP - HBOT
W = 6.0; H = W * (2 * YH) / span
fig = plt.figure(figsize=(W, H), dpi=400)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(L - HTOP, L - HBOT); ax.set_ylim(-YH, YH); ax.set_aspect("equal", adjustable="box")
fig.canvas.draw()
F.draw_structure(ax, YH + 0.30 * F.L_MOL)
for t in list(ax.texts):
    t.remove()
ax.axvspan(L, L + 20, color="#C8C3BE", zorder=4.4, lw=0)
ax.set_xlim(L - HTOP, L - HBOT); ax.set_ylim(-YH, YH); ax.axis("off")
fig.savefig("/home/claude/assets/substrate_strip_h.png", facecolor="white")
im = Image.open("/home/claude/assets/substrate_strip_h.png").convert("RGB").rotate(-90, expand=True)
im.save("/home/claude/assets/substrate_strip.png")
print("total", L, "tau_si", info["tau_si"], "size", im.size, "HTOP", HTOP, "HBOT", HBOT)
