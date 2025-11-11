

def crop(ds, latmin, latmax, lonmin, lonmax):
	ds_cropped = ds.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
	return ds_cropped
