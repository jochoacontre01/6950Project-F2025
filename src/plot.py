import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import addcopyfighandler
import sys

# -------------

ds = xr.load_dataset(r'/media/jochoa/DATA/Documentos/MUN Earth Sciences Masters Degree/000 - Courses/CMSC-6950_Comp_based_tools/Project/6950Project-F2025/data/monthly_historical_snow_depth_cesm2_1950-2014_01-12/snd_LImon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc', engine='h5netcdf')['snd']

world_boundaries = gpd.read_file(r'/media/jochoa/DATA/Documentos/MUN Earth Sciences Masters Degree/000 - Courses/CMSC-6950_Comp_based_tools/Project/6950Project-F2025/src/assets/world-administrative-boundaries-countries/world-administrative-boundaries-countries.shp')

lon = ds.coords['lon']
adjusted_lon = ((lon + 180) % 360) - 180

ds = ds.assign_coords(lon=adjusted_lon)
ds = ds.sortby(['lat', 'lon'], ascending=True)

ds += 1E-15
longitudes = ds['lon']
latitudes = ds['lat']

interest_point = [48.75976442880946, -55.85216447496896]
buffer_deg = 2.

# ds_loc = ds.sel(
# 	lat=slice(
# 		interest_point[0] - buffer_deg, interest_point[0] + buffer_deg,
# 	),
# 	lon=slice(
# 		interest_point[1] - buffer_deg, interest_point[1] + buffer_deg
# 	)
# )

ds_loc = ds.sel(lat=interest_point[0], lon=interest_point[1], method='nearest')
# 
year = 2000
# ds_filtered = ds[ds.time.dt.year > year].groupby('time.season').median(dim='time')
ds_filtered = ds_loc.groupby('time.season')['DJF']
print(ds_filtered)

plt.plot(ds_filtered)
plt.show()
sys.exit()

ax = world_boundaries.plot(linewidth=0.75, edgecolor='k', facecolor="#00000000")

toplot = np.where(np.isnan(ds_filtered), np.nan, np.log(ds_filtered))
im = plt.imshow(toplot, origin='lower', cmap='Blues', extent=(np.amin(longitudes), np.amax(longitudes), np.amin(latitudes), np.amax(latitudes)))
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title(f'Median snow depth before {year}')
# plt.xlim(interest_point[1]-buffer_deg, interest_point[1]+buffer_deg)
# plt.ylim(interest_point[0]-buffer_deg, interest_point[0]+buffer_deg)

cbar = plt.colorbar(im, label='meters')
vmin = np.nanmin(toplot)
vmax = np.nanmax(toplot)
ticks = np.arange(np.floor(vmin), np.ceil(vmax) + 1, 5)  
ticklabels = [f"$10^{{{int(tick)}}}$" if tick > 0 else f"$10^{{{int(tick)}}}$" for tick in ticks]  
cbar.set_ticks(ticks)  
cbar.set_ticklabels(ticklabels) 

# ds_filtered.plot(cmap='nipy_spectral')
fig = plt.gcf()
fig.set_size_inches(15,6)
plt.tight_layout()
plt.show()