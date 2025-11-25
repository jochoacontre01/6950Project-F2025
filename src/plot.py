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
savepath = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "docs/6950_project_latex/Fig"
)


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
    "data/snow_depth_monthly_historical_cesm2_1950-2015/snd_LImon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc",
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
    "data/snow_depth_monthly_ssp2_4_5_cesm2_2015-2100/snd_LImon_CESM2_ssp245_r4i1p1f1_gn_20150115-21001215.nc",
)

var_245 = os.path.basename(ds_path_245).split("_")[0]
ds_245 = load_preprocess(ds_path_245, interest_point, buffer_deg, var_245)
scenario_245 = match_scenario(ds_path_245).format()


# ? scenario_SSP3-7.0
ds_path_370 = os.path.join(
    os.path.dirname(__file__),
    "data/snow_depth_monthly_ssp3_7_0_cesm2_2015-2100/snd_LImon_CESM2_ssp370_r4i1p1f1_gn_20150115-21001215.nc",
)

var_370 = os.path.basename(ds_path_370).split("_")[0]
ds_370 = load_preprocess(ds_path_370, interest_point, buffer_deg, var_370)
scenario_370 = match_scenario(ds_path_370).format()

scenarios = [scenario_historical, scenario_245, scenario_370]

ds_hist_245 = xr.concat([ds_historical, ds_245], dim="time")


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
    ds_historical.resample(time="5YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_historical[-1] - base_year_historical[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_historical = PlotObject(difference, var_historical)


base_year_245 = (
    ds_245.resample(time="5YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_245[-1] - base_year_245[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_245 = PlotObject(difference, var_245)

base_year_370 = (
    ds_370.resample(time="5YE").mean(dim="time").groupby("time.season")["DJF"]
)
difference = base_year_370[-1] - base_year_370[0]
mask = np.isfinite(difference)
difference = xr.where(mask, difference, 0)
toplot_370 = PlotObject(difference, var_370)


# ! ###################################
# ! MAP PLOTTING

vmin = np.amin(np.stack([toplot_historical.data.values, toplot_245.data.values, toplot_370.data.values]).flatten())
vmax = np.amax(np.stack([toplot_historical.data.values, toplot_245.data.values, toplot_370.data.values]).flatten())
vmin = -vmax

toplot_historical.create_map(
    scenario="Historical",
    cpoint=interest_point,
    buffer=buffer_deg,
    # save_to=savepath + "/map_temp_hist.png",
    
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic',
    interpolation_stage='rgba'
)

toplot_245.create_map(
    scenario="SSP2-4.5",
    cpoint=interest_point,
    buffer=buffer_deg,
    # save_to=savepath + "/map_temp_245.png",
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic',
    interpolation_stage='rgba'
)

toplot_370.create_map(
    scenario="SSP3-7.0",
    cpoint=interest_point,
    buffer=buffer_deg,
    # save_to=savepath + "/map_temp_370.png",
    vmin=vmin,
    vmax=vmax,
    interpolation='bicubic',
    interpolation_stage='rgba'
)

# map_plot(toplot_370, scenario_370)

# ! -------------
# ! Time series plot of snow depth change

ds_hist_245_filtered = (
    ds_hist_245.resample(time="QS-DEC").mean()[::4].mean(dim=["lat", "lon"])
)
ds_historical_filtered = (
    ds_historical.resample(time="QS-DEC").mean()[::4].mean(dim=["lat", "lon"])
)
ds_245_filtered = ds_245.resample(time="QS-DEC").mean()[::4].mean(dim=["lat", "lon"])
ds_370_filtered = ds_370.resample(time="QS-DEC").mean()[::4].mean(dim=["lat", "lon"])

years_hist_245 = ds_hist_245_filtered.time.dt.year
years_historical = ds_historical_filtered.time.dt.year
years_245 = ds_245_filtered.time.dt.year
years_370 = ds_370_filtered.time.dt.year

years_245_n = np.arange(min(years_245), max(years_245) + 1)
coeff_245 = np.polyfit(years_245, ds_245_filtered, deg=5)
trend_245 = np.polyval(coeff_245, years_245_n)
# trend_245 = coeff_245[0]*years_245_n + coeff_245[1]

years_370_n = np.arange(min(years_370), max(years_370) + 1)
coeff_370 = np.polyfit(years_370, ds_370_filtered, deg=5)
trend_370 = np.polyval(coeff_370, years_370_n)
# trend_370 = coeff_370[0]*years_370_n + coeff_370[1]

fig = plt.figure(figsize=(12, 6))

# plt.plot(years_hist_245, ds_hist_245_filtered, "oy-", lw=1.5, label="Historical + SSP2-4.5")
plt.plot(years_245, trend_245, c='orange', ls="--", lw=1.5)
plt.plot(years_370, trend_370, c='r', ls="--", lw=1.5)
plt.plot(
    years_historical,
    ds_historical_filtered,
    "ok-",
    ms=5,
    alpha=0.5,
    lw=1.5,
    label="Historical",
)
plt.plot(years_245, ds_245_filtered, c="orange", alpha=0.5, lw=0.75, label="SSP2-4.5")
plt.plot(years_370, ds_370_filtered, c='r', alpha=0.5, lw=0.75, label="SSP3-7.0")
plt.xlabel("Year")

if var_historical == "snd":
    plt.ylabel("Depth (m)")
    plt.title(f"Snow depth change in Atlantic Canada\nScenario {scenario_historical}")
elif var_historical == "tas":
    plt.ylabel("Temperature (C)")
    plt.title(f"Temperature change in Atlantic Canada\nScenario {scenario_historical}")

plt.title("Average temperature in Atlantic Canada")
plt.gcf().set_size_inches(8, 6)
plt.tight_layout()
plt.legend()
# plt.savefig(f'{savepath}/temp_timeseries.png', dpi=150)
plt.show()