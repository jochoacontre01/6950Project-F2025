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


plt.style.use(['science','no-latex'])
matplotlib.rcParams.update({'font.size': 16})
# -------------

# ! -------------
# ! Data loading

ds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/snow_depth_monthly_ssp1_2_6_cesm2_2015-2050/snd_LImon_CESM2_ssp126_r4i1p1f1_gn_20150115-20501215.nc')
var = os.path.basename(ds_path).split("_")[0]
ds = xr.load_dataset(ds_path, engine='h5netcdf')[var]
if var == 'tas':
	ds = ds-273.15

wbound_path = os.path.join(os.path.dirname(__file__), 'assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp')
world_boundaries = gpd.read_file(wbound_path)


# ! -------------
# ! Dataset preprocessing
lon = ds.coords['lon']
adjusted_lon = ((lon + 180) % 360) - 180

ds = ds.assign_coords(lon=adjusted_lon)
ds = ds.sortby(['lat', 'lon'], ascending=True)

ds += 1E-15
longitudes = ds['lon']
latitudes = ds['lat']


# ! -------------
# ! Point of analysis (about center Newfoundland)
interest_point = [55.37437902920724, -60.67567886857576]
buffer_deg = 15.


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

im = plt.imshow(toplot, origin='lower', cmap=cmap, extent=(np.amin(longitudes), np.amax(longitudes), np.amin(latitudes), np.amax(latitudes)), norm=norm, interpolation='bicubic')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

if var == 'snd':
	plt.title('Changes in snow depth for the periods 1950-1980 and 2010-2015')
	cbar = plt.colorbar(im, label='meters')
elif var == 'tas':
	plt.title('Changes in temperature for the periods 1950-1980 and 2010-2015')
	cbar = plt.colorbar(im, label='C')

plt.xlim(interest_point[1]-buffer_deg, interest_point[1]+buffer_deg)
plt.ylim(interest_point[0]-buffer_deg, interest_point[0]+buffer_deg)

# ticks = np.arange(np.floor(vmin), np.ceil(vmax) + 1, 5)  
# ticklabels = [f"$10^{{{int(tick)}}}$" if tick > 0 else f"$10^{{{int(tick)}}}$" for tick in ticks]  
# cbar.set_ticks(ticks)  
# cbar.set_ticklabels(ticklabels) 

# ds_filtered.plot(cmap='nipy_spectral')
fig = plt.gcf()
fig.set_size_inches(8,6)
plt.tight_layout()
# plt.savefig('src/Fig/snow_change_map_atl_CA.png', dpi=150)
plt.show()


# ! -------------
# ! Time series plot of snow depth change
ds_loc_timeline = ds.sel(lat=slice(interest_point[0]-buffer_deg, interest_point[0]+buffer_deg), lon=slice(interest_point[1]-buffer_deg, interest_point[1]+buffer_deg))

# ds_filtered = ds_loc_timeline.groupby('time.season')['DJF'].mean(dim=['lat','lon'])
ds_filtered = ds_loc_timeline.resample(time='QS-DEC').mean()[::4].mean(dim=['lat','lon'])

years = ds_filtered.time.dt.year
plt.plot(years, ds_filtered, 'ok-')
plt.xlabel('Year')

if var == 'snd':
	plt.ylabel('Depth (m)')
	plt.title('Snow depth change in Atlantic Canada')
elif var == 'tas':
	plt.ylabel('Tenperature (C)')
	plt.title('Temperature change in Atlantic Canada')

plt.gcf().set_size_inches(8,6)
plt.tight_layout()
# plt.savefig('src/Fig/snow_change_timeseries_atl_CA.png', dpi=150)
plt.show()
