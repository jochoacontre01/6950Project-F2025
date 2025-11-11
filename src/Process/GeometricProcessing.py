

def crop(ds, latmin, latmax, lonmin, lonmax):
	ds_cropped = ds.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
	return ds_cropped

def adjust_coords(ds):
	lon = ds.coords['lon']
	adjusted_lon = ((lon + 180) % 360) - 180

	ds = ds.assign_coords(lon=adjusted_lon)
	ds = ds.sortby(['lat', 'lon'], ascending=True)

	return ds
