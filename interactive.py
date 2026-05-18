"""
Cette partie du programme est l'affichage de la simulation'
Ce programme gère le tableau, les sources d'ondes, les obstacles,
et l'animation de la simulation à l'aide de matplotlib.

C'est une version interactive de main.py
"""

import numpy as np # pour créer des tableaux
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

        self.sources = []
        self.screen_x = self.N - 2
        self.screen_signal = np.zeros(self.N)
        self.screen_samples = 0

        # état interaction souris
        self._shift_pressed = False
        self._mouse_pressed = False

        # couleur décor
        self.fig, (self.ax, self.ax_intensity) = plt.subplots(
            1,
            2,
            figsize=(12, 5),
            gridspec_kw={"width_ratios": [3, 2]}
        )

        # affichage et couleur écran
        self.ax.plot(
            [0, self.N - 1],
            [self.screen_x, self.screen_x],
            color="white",
            linestyle="--",
            linewidth=1.5
        )

        # affichage des sources
        self.source_display = self.ax.scatter([sy for _, sy in self.sources],
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

        # création de l'affichage pour les murs
        self.wall_rgba = np.zeros((self.N, self.N, 4), dtype=float)
        self.wall_display = self.ax.imshow(
            self.wall_rgba,
            origin="lower",
            zorder=2,
            extent=[0, self.N, 0, self.N]
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

        # connexion événements souris/clavier
        self.fig.canvas.mpl_connect("button_press_event", self._on_press)
        self.fig.canvas.mpl_connect("button_release_event", self._on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self._on_key_release)

        # animation de l'image
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            frames=frames,
            interval=ms,
            blit=False # self.update ne retourne pas la liste des elements changés, alors on sacrifie un peu de performance
        )

    def _event_to_grid(self, event):
        """Convertit un événement en coordonnées (row, col) dans la grille."""
        if event.inaxes is not self.ax:
            return None, None
        col = int(round(event.xdata))
        row = int(round(event.ydata))
        if 0 <= row < self.N and 0 <= col < self.N:
            return row, col
        return None, None

    def _on_key_press(self, event):
        """Callback pour les touches pressées"""
        if event.key == "shift":
            self._shift_pressed = True

    def _on_key_release(self, event):
        """Callback pour les touches lâchées"""
        if event.key == "shift":
            self._shift_pressed = False

    def _on_press(self, event):
        """Callback pour les clicks souris"""
        if event.button != 1:
            return
        self._mouse_pressed = True
        row, col = self._event_to_grid(event)
        if row is None:
            return
        if self._shift_pressed:
            self.mur[row, col] = 0
            self.onde[row, col] = 0
            self.onde_avant[row, col] = 0
            self._refresh_walls()
        else:
            self.sources.append((row, col))

    def _on_release(self, event):
        """Callback pour les desclicks souris"""
        if event.button == 1:
            self._mouse_pressed = False

    def _on_motion(self, event):
        """Callback pour les mouvements de la souris"""
        if not (self._mouse_pressed and self._shift_pressed):
            return
        row, col = self._event_to_grid(event)
        if row is None:
            return
        self.mur[row, col] = 0
        self.onde[row, col] = 0
        self.onde_avant[row, col] = 0
        self._refresh_walls()
    
    def _refresh_sources(self):
        """Rafraichit l'affichage des sources"""
        offsets = [(s[1], s[0]) for s in self.sources]
        self.source_display.set_offsets(offsets if offsets else np.empty((0, 2)))

    def _refresh_walls(self):
        """Rafraichit l'affichage des murs"""
        # masque comme self.mur, mais 0 == True et 1 == False
        blocked = self.mur == 0

        # toutes les cases où blocked est vrai, y mettre la valeur (1.0, 0.0, 0.0, 1.0)
        self.wall_rgba[..., 0] = np.where(blocked, 1.0, 0.0)
        self.wall_rgba[..., 1] = np.where(blocked, 0.0, 0.0)
        self.wall_rgba[..., 2] = np.where(blocked, 0.0, 0.0)
        self.wall_rgba[..., 3] = np.where(blocked, 1.0, 0.0)

        # mettre à jour l'affichage
        self.wall_display.set_data(self.wall_rgba)

    def inject_sources(self):
        """
        Ajoute sources sinusoïdales dans le tableau.

        Fonctionnement :
        - Source --> perturbation (sinusoïdale) --> par rapport au temps
        """

        for sx, sy in self.sources:
            self.onde[sx, sy] += np.sin(self.frame * 0.15)
        
        self._refresh_sources()

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