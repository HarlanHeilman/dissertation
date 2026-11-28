import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ["/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf","/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf",
          "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf","/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
          "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"]:
    fm.fontManager.addfont(f)
CRIMSON, DEEP, CLAY, BLUE, SKY, SLATE, INK = "#981E32", "#6C1524", "#D97757", "#2F5F8F", "#6A9BCC", "#5E6A71", "#1F1F1F"
plt.rcParams.update({
    "font.family": ["Caladea", "FreeSerif"], "font.size": 12, "mathtext.fontset": "custom",
    "mathtext.rm": "FreeSerif", "mathtext.it": "FreeSerif:italic", "mathtext.bf": "FreeSerif:bold",
    "axes.edgecolor": SLATE, "axes.labelcolor": INK, "xtick.color": SLATE, "ytick.color": SLATE,
    "xtick.labelcolor": INK, "ytick.labelcolor": INK, "axes.linewidth": 0.9,
    "axes.spines.top": False, "axes.spines.right": False, "xtick.direction": "out", "ytick.direction": "out",
    "savefig.transparent": True, "legend.frameon": False, "axes.titlesize": 13,
})
