import matplotlib.pyplot as plt
import numpy as np
import os
import geopandas as gpd
from matplotlib.colors import TwoSlopeNorm

wbound_path = os.path.join(os.path.dirname(__file__), 'assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp')
world_boundaries = gpd.read_file(wbound_path)

class PlotObject:
    def __init__(self, data, var):
        self.data = data
        self.var = var
        self.longitudes = data['lon']
        self.latitudes = data['lat']

    def create_map(self, scenario, cpoint, buffer):
        if self.data.ndim < 2:
            raise ValueError(
                f"Cannot create a map with data of shape {self.data.shape}"
            )

        fig = plt.figure(figsize=(9, 9))
        ax = fig.add_subplot()

        world_boundaries.plot(
            linewidth=0.75, edgecolor="k", facecolor="#00000000", ax=ax
        )
        vmax = np.amax(self.data)
        vmin = -vmax
        norm = TwoSlopeNorm(0, vmin, vmax)

        if self.var == "snd":
            cmap = "Spectral"
        elif self.var == "tas":
            cmap = "RdBu_r"

        im = ax.imshow(
            self.data,
            origin="lower",
            cmap=cmap,
            extent=(
                np.amin(self.longitudes),
                np.amax(self.longitudes),
                np.amin(self.latitudes),
                np.amax(self.latitudes),
            ),
            norm=norm,
            interpolation="bicubic",
            interpolation_stage="rgba",
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        if self.var == "snd":
            if scenario == "Historical":
                ax.set_title(
                    f"Changes in snow depth\nPeriods 1950-1960 and 2005-2015\nScenario {scenario}"
                )
            else:
                ax.set_title(
                    f"Changes in snow depth\nPeriods 2015-2025 and 2040-2050\nScenario {scenario}"
                )
            plt.colorbar(im, label="meters", shrink=0.75)

        elif self.var == "tas":
            if scenario == "Historical":
                ax.set_title(
                    f"Changes in temperature\nPeriods 1950-1960 and 2005-2015\nScenario {scenario}"
                )
            else:
                ax.set_title(
                    f"Changes in temperature\nPeriods 2015-2025 and 2040-2050\nScenario {scenario}"
                )
            plt.colorbar(im, label="C", shrink=0.75)

        ax.set_xlim(
            cpoint[1] - buffer * 0.98, cpoint[1] + buffer * 0.98
        )
        ax.set_ylim(
            cpoint[0] - buffer * 0.98, cpoint[0] + buffer * 0.98
        )

        plt.tight_layout()
        plt.show()
