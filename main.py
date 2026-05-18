"""
Cette partie du programme est l'affichage de la simulation'
Ce programme gère le tableau, les sources d'ondes, les obstacles,
et l'animation de la simulation à l'aide de matplotlib.
"""

import numpy as  np # pour créer des tableaux
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation # animation
from huygens import step_wave


class Huygens:
    """
    Classe servant à simuler une propagation d'onde en 2D
    """

    def __init__(self, frames=900, ms=25):
        """
        Initialise le tableau, les paramètres, le mur et l'affichage.
        """

        # paramètres physiques:
        self.N = 200 # taille tableau

        self.onde = np.zeros((self.N, self.N))
        self.onde_avant = np.zeros_like(self.onde)

        self.c = 1.3 # milieu
        self.dt = 0.5 # temps (intervalle)
        self.dx = 1 # espace (intervalle)

        self.mur = np.ones((self.N, self.N))

        self.fente_x = 100 # coord. verticale fente
        slit_width = 20
        slit_gap = 20
        total_width = 3 * slit_width + 2 * slit_gap
        start = (self.N - total_width) // 2
        self.coords = [
            (start + i * (slit_width + slit_gap), start + i * (slit_width + slit_gap) + slit_width)
            for i in range(3)
        ]

        for y in range(self.N):
            self.mur[self.fente_x, y] = 0

        for y1, y2 in self.coords:
            for y in range(y1, y2):
                self.mur[self.fente_x, y] = 1

        self.sources = [
            (30, (y1 + y2) // 2)
            for y1, y2 in self.coords
        ] # coords. x y sources
        self.screen_x = self.N - 2
        self.screen_signal = np.zeros(self.N)
        self.screen_samples = 0

        # couleur décor
        self.fig, (self.ax, self.ax_intensity) = plt.subplots(
            1,
            2,
            figsize=(12, 5),
            gridspec_kw={"width_ratios": [3, 2]}
        )

        # affichage et couleur fentes
        x0 = 0
        for x1, x2 in self.coords:
            self.ax.plot([x0, x1], [self.fente_x, self.fente_x], color="red", linewidth=2)
            x0 = x2
        self.ax.plot([x0, self.N], [self.fente_x, self.fente_x], color="red", linewidth=2)
        self.ax.plot(
            [0, self.N - 1],
            [self.screen_x, self.screen_x],
            color="white",
            linestyle="--",
            linewidth=1.5
        )

        # affichage des sources
        self.ax.scatter([sy for _, sy in self.sources],
                        [sx for sx, _ in self.sources],
                        color="white", s=20, zorder=3)

        # personnalisation image
        self.im = self.ax.imshow(
            self.onde,
            cmap="viridis", # colorimétrie de l'image
            vmin=-1,
            vmax=1,
            origin="lower"
        )

        # échelle ampitudes
        self.fig.colorbar(self.im, ax=self.ax)

        # titre image
        self.ax.set_title(
            "Simulation de Huygens - ondes passant par des fentes",
        )
        self.ax.set_xlabel("Position horizontale")
        self.ax.set_ylabel("Position verticale")

        self.intensity_x = np.arange(self.N)
        self.intensity_line, = self.ax_intensity.plot(
            self.intensity_x,
            np.zeros(self.N),
            color="gold"
        )
        self.ax_intensity.set_xlim(0, self.N - 1)
        self.ax_intensity.set_ylim(0, 1.05)
        self.ax_intensity.set_title("Intensité normalisée sur l'écran")
        self.ax_intensity.set_xlabel("Position sur l'écran")
        self.ax_intensity.set_ylabel("Intensité normalisée")

        # animation de l'image
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            frames=frames,
            interval=ms,
            blit=False # self.update ne retourne pas la liste des elements changés, alors on sacrifie un peu de performance
        )

    def inject_sources(self):
        """
        Ajoute sources sinusoïdales dans le tableau.

        Fonctionnement :
        - Source --> perturbation (sinusoïdale) --> par rapport au temps
        """

        for sx, sy in self.sources:
            self.onde[sx, sy] += np.sin(self.frame * 0.15)

    def update(self, frame):
        """
        Mise à jour de l'animation

        Paramètres :
        frame  : numéro de l'image courante

        Fonctionnement :
        - Fonction inject_sources()
        - Calcul onde_après
        - Mise à jour l'affichage
        """

        self.frame = frame

        self.inject_sources()

        # calcul nouvelle onde
        onde_apres = step_wave(
            self.onde,
            self.onde_avant,
            self.c,
            self.dt,
            self.dx,
            self.mur
        )

        # avant --> maintenant // maintenant --> après
        self.onde_avant = self.onde
        self.onde = onde_apres

        self.screen_signal += self.onde[self.screen_x, :] ** 2
        self.screen_samples += 1
        intensity = self.screen_signal / self.screen_samples
        intensity_max = np.max(intensity)

        if intensity_max > 0:
            displayed_intensity = intensity / intensity_max
        else:
            displayed_intensity = intensity

        self.im.set_array(self.onde)
        self.intensity_line.set_ydata(displayed_intensity)

        return [self.im, self.intensity_line]

if __name__ == "__main__":
    sim = Huygens()
    plt.show() # afficher l'image