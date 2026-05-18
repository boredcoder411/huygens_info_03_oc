"""
Cette partie du programme sert uniquement pour générer les figures
pour la présentation
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from main import Huygens

# constantes pour les dossiers qu'on va créer
ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
MPLCONFIG = FIGURES / ".mplconfig"

# s'assurer que nos dossiers de sortie existent
FIGURES.mkdir(exist_ok=True)
MPLCONFIG.mkdir(exist_ok=True)

# configuration matplotlib via des variables d'environement
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIG))

def save_geometry():
    """Fonction qui exporte seulement le 'setup' ou la géometrie de la simulation"""
    sim = Huygens()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor("#0f2230")

    x0 = 0
    for x1, x2 in sim.coords:
        ax.plot([x0, x1], [sim.fente_x, sim.fente_x], color="#ff5a36", linewidth=4)
        x0 = x2
    ax.plot([x0, sim.N], [sim.fente_x, sim.fente_x], color="#ff5a36", linewidth=4, label="Barrière")

    source_x = [sy for _, sy in sim.sources]
    source_y = [sx for sx, _ in sim.sources]
    ax.scatter(source_x, source_y, s=80, color="#ffe066", edgecolors="black", linewidths=0.8, zorder=3, label="Sources")

    ax.plot([0, sim.N - 1], [sim.screen_x, sim.screen_x], color="white", linestyle="--", linewidth=2, label="Écran de détection")

    ax.annotate(
        "Propagation",
        xy=(source_x[1], sim.fente_x - 5),
        xytext=(source_x[1], 55),
        color="white",
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "white", "lw": 1.5}
    )
    ax.text(10, sim.screen_x + 3, "Écran", color="white", fontsize=12)
    ax.text(10, sim.fente_x + 4, "Barrière à trois fentes centrées", color="#ff5a36", fontsize=12)

    ax.set_title("Géométrie de la simulation", color="white")
    ax.set_xlim(0, sim.N - 1)
    ax.set_ylim(0, sim.N - 1)
    ax.set_xlabel("Position horizontale", color="white")
    ax.set_ylabel("Position verticale", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "geometry.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    plt.close(sim.fig)

def advance(sim, frames):
    """Fonction pour faire avancer la simulation de n étapes (paramètre frames)"""
    for frame in range(frames):
        sim.update(frame)

def save_snapshot(filename, frames, title):
    """Fonction pour sauvegarder une capture du champ + détecteur à n étapes"""
    sim = Huygens()
    advance(sim, frames)
    sim.ax.set_title(title)
    sim.fig.tight_layout()
    sim.fig.savefig(FIGURES / filename, dpi=200, bbox_inches="tight")
    plt.close(sim.fig)

def save_intensity_profile(frames=700):
    """Fonction qui sauvegarde seulement la réponse du détecteur à n étapes"""
    sim = Huygens()
    advance(sim, frames)

    # traitement des données de l'écran
    intensity = sim.screen_signal / max(sim.screen_samples, 1)
    intensity_max = max(float(np.max(intensity)), 1e-12)
    normalized = intensity / intensity_max

    # affichage
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(np.arange(sim.N), normalized, color="black", linewidth=1.8)
    ax.set_title(f"Intensité normalisée sur l'écran après {frames} images")
    ax.set_xlabel("Position sur l'écran")
    ax.set_ylabel("Intensité normalisée")
    ax.set_xlim(0, sim.N - 1)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "intensity_profile.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    plt.close(sim.fig)

def save_video(frames, fps):
    """Fonction qui sauvegarde la video de la simulation"""
    # conversion de fps à intervalle entre frame en ms
    ms = 1000 / fps

    sim = Huygens(frames, ms)

    sim.anim.save(FIGURES / "animation.mp4", writer="ffmpeg", fps=fps)
    plt.close(sim.fig)

if __name__ == "__main__":
    save_geometry()
    save_snapshot("snapshot_mid.png", 300, "Champ d'onde et réponse du détecteur à 300 images")
    save_snapshot("snapshot_late.png", 700, "Champ d'onde et réponse du détecteur à 700 images")
    save_intensity_profile()
    save_video(1000, 60)