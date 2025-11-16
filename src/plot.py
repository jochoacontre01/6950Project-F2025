import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import geopandas as gpd
import addcopyfighandler
import scienceplots
import matplotlib
import sys
import os

from Process.GeometricProcessing import crop, adjust_coords
from Process.StringOps import match_scenario
from Process.Plotting import PlotObject

plt.style.use(["science", "no-latex"])
matplotlib.rcParams.update({"font.size": 16})
# -------------
# ! -------------
# ! Point of analysis (about central Newfoundland) as (lat, lon)
interest_point = [55.37437902920724, -60.67567886857576]
buffer_deg = 15.0


def load_preprocess(path, center_point, buffer, var):
    bbox = [
        center_point[0] - buffer,
        center_point[0] + buffer,
        center_point[1] - buffer,
        center_point[1] + buffer,
    ]

    # ! Load dataset with xarray and perform basic preprocessing
    ds = xr.load_dataset(path, engine="h5netcdf")[var]
    if var == "tas":
        ds = ds - 273.15
    ds = adjust_coords(ds)
    ds = crop(ds, *bbox)
    ds += 1e-15  # ? Add stability constant

    return ds


# ! ###################################
# ! DATA LOADING


# ? scenario_historical
ds_path_historical = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_historical_cesm2_1950-2015/tas_Amon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc",
)

var_historical = os.path.basename(ds_path_historical).split("_")[0]
ds_historical = load_preprocess(
    ds_path_historical, interest_point, buffer_deg, var_historical
)

scenario_historical = match_scenario(ds_path_historical).format()
if scenario_historical is None:
    scenario_historical = "Historical"


# ? scenario_SSP2-4.5
ds_path_245 = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_ssp2_4_5_cesm2_2015-2050/tas_Amon_CESM2_ssp245_r4i1p1f1_gn_20150115-20501215.nc",
)

var_245 = os.path.basename(ds_path_245).split("_")[0]
ds_245 = load_preprocess(ds_path_245, interest_point, buffer_deg, var_245)
scenario_245 = match_scenario(ds_path_245).format()


# ? scenario_SSP3-7.0
ds_path_370 = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_ssp3_7_0_cesm2_2015-2050/tas_Amon_CESM2_ssp370_r4i1p1f1_gn_20150115-20501215.nc",
)

var_370 = os.path.basename(ds_path_370).split("_")[0]
ds_370 = load_preprocess(ds_path_370, interest_point, buffer_deg, var_370)
scenario_370 = match_scenario(ds_path_370).format()

scenarios = [scenario_historical, scenario_245, scenario_370]

# ! ###################################
# ! Load world bounds dataset
wbound_path = os.path.join(
    os.path.dirname(__file__),
    "assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp",
)
world_boundaries = gpd.read_file(wbound_path)

longitudes = ds_historical["lon"]
latitudes = ds_historical["lat"]


# ! ###################################
# ! STATISTICAL ANALYSIS STARTS

# ! -------------
# ? Creation of 30-year mean for long-term change assessment
base_year_historical = (
    ds_historical.resample(time="10YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_historical[-1] - base_year_historical[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_historical = PlotObject(difference, var_historical)


base_year_245 = (
    ds_245.resample(time="10YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_245[-1] - base_year_245[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_245 = PlotObject(difference, var_245)

base_year_370 = (
    ds_370.resample(time="10YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_370[-1] - base_year_370[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_370 = PlotObject(difference, var_370)


# ! ###################################
# ! MAP PLOTTING

toplot_historical.create_map(
    scenario="Historical", cpoint=interest_point, buffer=buffer_deg
)

toplot_245.create_map(
    scenario="SSP2-4.5", cpoint=interest_point, buffer=buffer_deg
)

toplot_370.create_map(
    scenario="SSP3-7.0", cpoint=interest_point, buffer=buffer_deg
)

# map_plot(toplot_370, scenario_370)

# ! -------------
# ! Time series plot of snow depth change

ds_historical_filtered = (
    ds_historical.resample(time="QS-DEC")
    .max(
        
    )[::4]
    .max( dim=["lat", "lon"])
)
ds_245_filtered = (
    ds_245.resample(time="QS-DEC")
    .max(
        
    )[::4]
    .max( dim=["lat", "lon"])
)
ds_370_filtered = (
    ds_370.resample(time="QS-DEC")
    .max(
        
    )[::4]
    .max( dim=["lat", "lon"])
)

years_historical = ds_historical_filtered.time.dt.year
years_245 = ds_245_filtered.time.dt.year
years_370 = ds_370_filtered.time.dt.year

fig = plt.figure(figsize=(12,6))
plt.plot(years_historical, ds_historical_filtered, "k-", lw=1.5, label="Historical")
plt.plot(years_245, ds_245_filtered, "g-", lw=1.5, label="SSP2-4.5")
plt.plot(years_370, ds_370_filtered, "b-", lw=1.5, label="SSP3-7.0")
plt.xlabel("Year")

if var_historical == "snd":
    plt.ylabel("Depth (m)")
    plt.title(f"Snow depth change in Atlantic Canada\nScenario {scenario_historical}")
elif var_historical == "tas":
    plt.ylabel("Tenperature (C)")
    plt.title(f"Temperature change in Atlantic Canada\nScenario {scenario_historical}")

plt.gcf().set_size_inches(8, 6)
plt.tight_layout()
plt.legend()
# plt.savefig('src/Fig/snow_change_timeseries_atl_CA.png', dpi=150)
plt.show()
