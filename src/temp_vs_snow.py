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
import seaborn as sns

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

# ! TEMPERATURE 
# ? scenario_historical
ds_path_historical_temp = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_historical_cesm2_1950-2015/tas_Amon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc",
)

var_historical_temp = os.path.basename(ds_path_historical_temp).split("_")[0]
ds_historical_temp = load_preprocess(
    ds_path_historical_temp, interest_point, buffer_deg, var_historical_temp
)

scenario_historical_temp = match_scenario(ds_path_historical_temp).format()
if scenario_historical_temp is None:
    scenario_historical_temp = "Historical"


# ! SNOW DEPTH 
# ? scenario_historical
ds_path_historical_snow = os.path.join(
    os.path.dirname(__file__),
    "data/snow_depth_monthly_historical_cesm2_1950-2015/snd_LImon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc",
)

var_historical_snow = os.path.basename(ds_path_historical_snow).split("_")[0]
ds_historical_snow = load_preprocess(
    ds_path_historical_snow, interest_point, buffer_deg, var_historical_snow
)

scenario_historical_snow = match_scenario(ds_path_historical_snow).format()
if scenario_historical_snow is None:
    scenario_historical_snow = "Historical"


# ! ###################################
# ! DATA PREPARATION
ds_historical_filtered_temp = ds_historical_temp.resample(time="QS-DEC").mean()[::4]#.mean(dim=["lat", "lon"])
ds_historical_filtered_snow = ds_historical_snow.resample(time="QS-DEC").mean()[::4]#.mean(dim=["lat", "lon"])

fig = plt.figure(figsize=(12, 6))
sns.regplot(    
    x=ds_historical_filtered_temp.values.flatten(),
    y=np.where(ds_historical_filtered_snow.values>1.5, np.nan, ds_historical_filtered_snow.values).flatten(),
    line_kws={
        'color':'r',
        'linestyle':'--'
    },
    scatter_kws={
        's':5,
        'color':"#949494",
        'alpha':0.2
    }
)
plt.xlabel('Temperature (C)')
plt.ylabel('Snow depth (m)')
plt.title('Relationship between temperature and snow depth')
plt.tight_layout()
plt.savefig(f'{savepath}/regplot2.png', dpi=150)
plt.show()

