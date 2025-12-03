import matplotlib.pyplot as plt
import numpy as np
import os
import geopandas as gpd
from matplotlib.colors import TwoSlopeNorm, SymLogNorm
from warnings import warn
import xarray as xr
from cmocean import cm
from shapely.geometry import Polygon


wbound_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp",
)
world_boundaries = gpd.read_file(wbound_path)


class PlotObject:
    def __init__(self, data, var):
        self.data = data
        self.var = var
        self.is_xarray = None

        if not isinstance(data, xr.DataArray):
            warn(
                "The input data is not xarray, some functions may not work properly",
                category=RuntimeWarning,
            )
            self.is_xarray = False
            self.longitudes = None
            self.latitudes = None
        else:
            self.is_xarray = True
            self.longitudes = data["lon"]
            self.latitudes = data["lat"]

    def create_map(self, scenario, cpoint, buffer, save_to=None, log=False, **kwargs):
        if self.data.ndim < 2:
            raise ValueError(
                f"Cannot create a map with data of shape {self.data.shape}"
            )
            
        if not self.is_xarray:
            raise ValueError(
				"Data is not of type xarray, cannot create map"
			)

        fig = plt.figure(figsize=(9, 9))
        ax = fig.add_subplot()

        map_extent = Polygon([
            (np.amin(self.longitudes), np.amin(self.latitudes)),
            (np.amax(self.longitudes), np.amin(self.latitudes)),
            (np.amax(self.longitudes), np.amax(self.latitudes)),
            (np.amin(self.longitudes), np.amax(self.latitudes)),
        ])

        land_geom = world_boundaries.union_all()

        water_geom = map_extent.difference(land_geom)
        gpd.GeoSeries(water_geom).plot(ax=ax, color='#a6cee3', zorder=1)

        world_boundaries.plot(
            linewidth=0.5, edgecolor="#000000", facecolor="#00000000", ax=ax
        )

        if "vmin" not in list(kwargs.keys()):
            vmax = np.quantile(self.data, 0.75)
            vmin = -vmax
        else:
            vmin = kwargs["vmin"]
            vmax = kwargs["vmax"]
        norm = TwoSlopeNorm(0, vmin, vmax) if not log else SymLogNorm(vmin=vmin, vmax=vmax, linthresh=1E-3)

        if self.var == "snd":
            cmap = "PuOr"
            self.data = xr.where(self.data == 0, np.nan, self.data)
        elif self.var == "tas":
            cmap = cm.balance

        print(vmax, vmin)
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
            **kwargs
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        if self.var == "snd":
            if scenario == "Historical":
                ax.set_title(
                    f"Changes in snow depth\nPeriods 1950-1955 against 2010-2015\nScenario {scenario}"
                )
            else:
                ax.set_title(
                    f"Changes in snow depth\nPeriods 2015-2020 against 2095-2100\nScenario {scenario}"
                )
            plt.colorbar(im, label="meters", shrink=0.75)

        elif self.var == "tas":
            if scenario == "Historical":
                ax.set_title(
                    f"Changes in temperature\nPeriods 1950-1955 against 2010-2015\nScenario {scenario}"
                )
            else:
                ax.set_title(
                    f"Changes in temperature\nPeriods 2015-2020 against 2095-2100\nScenario {scenario}"
                )
            plt.colorbar(im, label="C", shrink=0.75)

        ax.set_xlim(cpoint[1] - buffer * 0.98, cpoint[1] + buffer * 0.98)
        ax.set_ylim(cpoint[0] - buffer * 0.98, cpoint[0] + buffer * 0.98)

        plt.tight_layout()
        if save_to is not None:
            plt.savefig(save_to)
        plt.show()
