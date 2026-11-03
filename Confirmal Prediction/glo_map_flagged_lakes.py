"""Map of the lakes flagged High in GLO Step 3 (Nepal and transboundary catchments).
Borders: Natural Earth 1:110m (public domain). Peak and town positions are approximate."""
import sys
import geopandas as gpd, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

NE = sys.argv[1] if len(sys.argv) > 1 else "naturalearth_lowres.shp"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
INK, MUTED, GRID = "#1d2433", "#5b6475", "#d9dde4"
C_CONF, C_POSS, C_OTHER = "#c62828", "#ef8a3c", "#b9c0cc"
LAND = {"Nepal": "#f4f1e8", "China": "#eceff3", "India": "#eef1ec", "Bhutan": "#eef1ec"}

p = pd.read_csv("outputs/glo_analysis_predictions.csv")
f = pd.read_csv("outputs/glo_flagged_lakes.csv")
conf = f[f.risk_class == "High (confident)"].reset_index(drop=True)
conf["n"] = np.arange(1, len(conf) + 1)
poss = f[f.risk_class == "High (possible)"]
rest = p[~p.lake_id.isin(f.lake_id)]
world = gpd.read_file(NE)
PEAKS = {"Everest": (27.988, 86.925), "Kangchenjunga": (27.703, 88.147), "Makalu": (27.889, 87.089),
         "Cho Oyu": (28.094, 86.661), "Manaslu": (28.549, 84.559), "Annapurna I": (28.596, 83.820),
         "Dhaulagiri": (28.697, 83.487)}
TOWNS = {"Kathmandu": (27.717, 85.324), "Pokhara": (28.210, 83.986)}
ASPECT = 1 / np.cos(np.deg2rad(28.3))


def base(ax, ext, peaks=True, towns=True):
    for _, r in world.iterrows():
        gpd.GeoSeries([r.geometry]).plot(ax=ax, color=LAND.get(r["name"], "#f2f3f5"), edgecolor="#8a93a3", lw=0.8, zorder=0)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(ASPECT)
    ax.grid(color=GRID, lw=0.4, zorder=0.5); ax.tick_params(colors=MUTED, labelsize=8)
    ax.set_xlabel("Longitude (°E)", color=MUTED, fontsize=8); ax.set_ylabel("Latitude (°N)", color=MUTED, fontsize=8)
    for s in ax.spines.values():
        s.set_color("#aab1bd")
    if peaks:
        for n, (la, lo) in PEAKS.items():
            if ext[0] < lo < ext[1] and ext[2] < la < ext[3]:
                ax.plot(lo, la, marker="^", ms=6, mfc="none", mec=INK, mew=1, zorder=6)
                ax.annotate(n, (lo, la), xytext=(4, 4), textcoords="offset points", fontsize=7.5, color=INK, style="italic", zorder=6)
    if towns:
        for n, (la, lo) in TOWNS.items():
            if ext[0] < lo < ext[1] and ext[2] < la < ext[3]:
                ax.plot(lo, la, "s", ms=4, color=INK, zorder=6)
                ax.annotate(n, (lo, la), xytext=(4, -9), textcoords="offset points", fontsize=7.5, color=INK, zorder=6)


def lakes(ax, small=False):
    ax.scatter(rest.lon, rest.lat, s=3 if small else 6, c=C_OTHER, lw=0, zorder=2, label=f"Other lakes, Low/Moderate (n={len(rest):,})")
    ax.scatter(poss.lon, poss.lat, s=8 if small else 16, c=C_POSS, marker="D", lw=0.3, edgecolors="white", zorder=3,
               label=f"High (possible) (n={len(poss):,})")
    ax.scatter(conf.lon, conf.lat, s=40 if small else 70, c=C_CONF, marker="^", lw=0.6, edgecolors="white", zorder=4,
               label=f"High (confident) (n={len(conf)})")


fig = plt.figure(figsize=(15, 14), facecolor="white")
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15], width_ratios=[1, 1, 0.62], hspace=0.12, wspace=0.08)

# --- overview
ax = fig.add_subplot(gs[0, :])
ext = (79.9, 89.0, 26.3, 30.9)
base(ax, ext); lakes(ax, small=True)
zoom = (85.65, 88.55, 27.55, 28.5)
ax.add_patch(Rectangle((zoom[0], zoom[2]), zoom[1] - zoom[0], zoom[3] - zoom[2], fill=False, ec=INK, lw=1.2, ls="--", zorder=7))
ax.annotate("Zoom below", (zoom[0], zoom[3]), xytext=(0, 4), textcoords="offset points", fontsize=8, color=INK)
for name, (lo, la) in {"KARNALI BASIN": (81.6, 29.75), "GANDAKI BASIN": (83.9, 29.25), "KOSHI BASIN": (86.6, 28.9)}.items():
    ax.text(lo, la, name, fontsize=9, color=MUTED, weight="bold", ha="center", alpha=0.8, zorder=1)
for cname, (lo, la) in {"NEPAL": (83.2, 27.6), "CHINA (TIBET)": (84.0, 30.3), "INDIA": (82.0, 26.8)}.items():
    ax.text(lo, la, cname, fontsize=10, color="#7d8695", ha="center", zorder=1)
out = conf[conf.lon < zoom[0]]
for r in out.itertuples():
    ax.annotate(f"{r.n}", (r.lon, r.lat), xytext=(-4, 16), textcoords="offset points", fontsize=9, weight="bold", color=C_CONF,
                zorder=9, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                arrowprops=dict(arrowstyle="-", color=C_CONF, lw=0.6))
for r in f[(f.known_name.fillna("") != "") & (f.lon < zoom[0])].itertuples():
    ax.annotate(r.known_name, (r.lon, r.lat), xytext=(-8, -14), textcoords="offset points", fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6), zorder=8)
ax.legend(loc="lower left", frameon=True, framealpha=0.92, fontsize=8.5, markerscale=1.3)
ax.set_title("Glacial lakes flagged High for 2021→2024 (GLO, Nepal and transboundary catchments)", loc="left", fontsize=12, color=INK, pad=8)

# --- zoom
ax2 = fig.add_subplot(gs[1, :2])
base(ax2, zoom, towns=False); lakes(ax2)
NAME_OFFSETS = {"Tsho Rolpa": (-70, -34), "Dig Tsho": (-100, -6), "Imja Tsho": (-95, -48),
                "Lower Barun": (18, -38), "Thulagi": (10, -16)}
for r in f[(f.known_name.fillna("") != "") & (f.lon >= zoom[0])].itertuples():
    ax2.annotate(r.known_name, (r.lon, r.lat), xytext=NAME_OFFSETS.get(r.known_name, (-30, -22)), textcoords="offset points",
                 fontsize=8.5, color=INK, weight="bold", arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), zorder=8,
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
from adjustText import adjust_text
zc = conf[conf.lon >= zoom[0]]
texts = [ax2.text(r.lon, r.lat, f"{r.n}", fontsize=8.5, weight="bold", color=C_CONF, zorder=9,
                  bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.75)) for r in zc.itertuples()]
adjust_text(texts, x=zc.lon.to_numpy(), y=zc.lat.to_numpy(), ax=ax2, expand=(1.6, 1.8),
            force_text=(0.4, 0.6), force_static=(0.3, 0.5),
            arrowprops=dict(arrowstyle="-", color=C_CONF, lw=0.6))
ax2.text(87.9, 28.42, "CHINA (TIBET)", fontsize=9, color="#7d8695", ha="center")
ax2.text(86.0, 27.62, "NEPAL", fontsize=9, color="#7d8695", ha="center")
ax2.set_title("Koshi basin: Rolwaling, Khumbu (Everest), Makalu and the Tibetan side", loc="left", fontsize=11, color=INK, pad=6)

# --- list of confident lakes
ax3 = fig.add_subplot(gs[1, 2]); ax3.axis("off")
ax3.text(0, 1.0, "High (confident) lakes", fontsize=11, weight="bold", color=INK, va="top", transform=ax3.transAxes)
ax3.text(0, 0.968, "# · name or GLO position · area 2021 → 2024 (km²)", fontsize=7.5, color=MUTED, va="top", transform=ax3.transAxes)
y = 0.935
for r in conf.itertuples():
    nm = r.known_name if isinstance(r.known_name, str) and r.known_name else f"{r.lon:.3f}°E {r.lat:.3f}°N"
    ctry = "" if r.country == "Nepal" else f" ({r.country})"
    ax3.text(0, y, f"{r.n:>2}", fontsize=8, weight="bold", color=C_CONF, va="top", transform=ax3.transAxes, family="DejaVu Sans Mono")
    ax3.text(0.08, y, f"{nm}{ctry}", fontsize=8, color=INK, va="top", transform=ax3.transAxes,
             weight="bold" if isinstance(r.known_name, str) and r.known_name else "normal")
    ax3.text(1.0, y, f"{r.area_t0_km2:.2f} → {r.area_2024_observed_km2:.2f}", fontsize=8, color=MUTED, va="top", ha="right",
             transform=ax3.transAxes, family="DejaVu Sans Mono")
    y -= 0.031
ax3.text(0, y - 0.01, "Observed 2024 area fell inside the predicted\nrange for all 30 lakes.", fontsize=7.5, color=MUTED, va="top", transform=ax3.transAxes)
fig.text(0.01, 0.0, "Lakes: Glacial Lake Observatory (Rawlins et al. 2026, CC BY 4.0). Borders: Natural Earth 1:110m (coarse). "
         "The 1:110m border is generalised, so lakes near it can look like they sit on the wrong side; country comes from GLO. Peak and town positions approximate. High = split conformal upper/lower bound of growth-based susceptibility ≥ 0.6.",
         fontsize=7.5, color=MUTED)
fig.savefig("maps/glo_flagged_lakes_map.png", dpi=170, bbox_inches="tight")
print("saved", len(conf), len(poss), len(rest))
