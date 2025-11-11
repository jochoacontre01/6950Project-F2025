import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import geopandas as gpd
import addcopyfighandler
import scienceplots
import matplotlib
from numpy import fft
import sys
import os
import re

from Process.GeometricProcessing import crop, adjust_coords
from Process.StringOps import match_scenario

plt.style.use(['science','no-latex'])
matplotlib.rcParams.update({'font.size': 16})
# -------------

# ! -------------
# ! Data loading

ds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/snow_depth_monthly_historical_cesm2_1950-2015/snd_LImon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc')
var = os.path.basename(ds_path).split("_")[0]

scenario = match_scenario(ds_path).format()
if scenario is None:
	scenario = 'Historical'


ds = xr.load_dataset(ds_path, engine='h5netcdf')[var]
if var == 'tas':
	ds = ds-273.15

wbound_path = os.path.join(os.path.dirname(__file__), 'assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp')
world_boundaries = gpd.read_file(wbound_path)

# ! -------------
# ! Point of analysis (about central Newfoundland) as (lat, lon)
interest_point = [55.37437902920724, -60.67567886857576]
buffer_deg = 15.0
bbox = [interest_point[0] - buffer_deg, interest_point[0] + buffer_deg, interest_point[1] - buffer_deg, interest_point[1] + buffer_deg]

# ! -------------
# ! Dataset preprocessing
ds = adjust_coords(ds)
ds = crop(ds, *bbox)

ds += 1E-15
longitudes = ds['lon']
latitudes = ds['lat']


# ! -------------
# ! Creation of 30-year mean for long-term change assessment
base_year = ds.resample(time='30YE').mean(dim='time').groupby('time.season')['DJF']
difference = base_year[2] - base_year[0]


# ! -------------
# ! Map plotting
ax = world_boundaries.plot(linewidth=0.75, edgecolor='k', facecolor="#00000000")

# toplot = np.where(np.isnan(difference), np.nan, np.log(difference))
mask = np.isfinite(difference)
difference = np.where(mask, difference, 0)
toplot = difference

vmax = np.amax(toplot)
vmin = -vmax
norm = TwoSlopeNorm(0, vmin, vmax)
# toplot = np.clip(toplot, np.quantile(toplot, 0.25), np.quantile(toplot, 0.75))

if var == 'snd':
	cmap = 'winter'
elif var == 'tas':
	cmap = 'RdBu_r'

im = plt.imshow(toplot, origin='lower', cmap=cmap, extent=(np.amin(longitudes), np.amax(longitudes), np.amin(latitudes), np.amax(latitudes)), norm=norm, interpolation='bicubic', interpolation_stage='rgba')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

if var == 'snd':
	plt.title(f'Changes in snow depth for the periods 1950-1980 and 2010-2015\nScenario {scenario}')
	cbar = plt.colorbar(im, label='meters')
elif var == 'tas':
	plt.title(f'Changes in temperature for the periods 1950-1980 and 2010-2015\nScenario {scenario}')
	cbar = plt.colorbar(im, label='C')

plt.xlim(interest_point[1]-buffer_deg*0.98, interest_point[1]+buffer_deg*0.98)
plt.ylim(interest_point[0]-buffer_deg*0.98, interest_point[0]+buffer_deg*0.98)

fig = plt.gcf()
fig.set_size_inches(8,6)
plt.tight_layout()
# plt.savefig('src/Fig/snow_change_map_atl_CA.png', dpi=150)
plt.show()


# ! -------------
# ! Time series plot of snow depth change

ds_filtered = ds.resample(time='QS-DEC').mean()[::4].mean(dim=['lat','lon'])

years = ds_filtered.time.dt.year
plt.plot(years, ds_filtered, 'ok-')
plt.xlabel('Year')

if var == 'snd':
	plt.ylabel('Depth (m)')
	plt.title(f'Snow depth change in Atlantic Canada\nScenario {scenario}')
elif var == 'tas':
	plt.ylabel('Tenperature (C)')
	plt.title(f'Temperature change in Atlantic Canada\nScenario {scenario}')

plt.gcf().set_size_inches(8,6)
plt.tight_layout()
# plt.savefig('src/Fig/snow_change_timeseries_atl_CA.png', dpi=150)
plt.show()
