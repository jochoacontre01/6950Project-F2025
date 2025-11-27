import xarray as xr

def crop(ds, latmin, latmax, lonmin, lonmax):
	ds_cropped = ds.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
	return ds_cropped

def adjust_coords(ds):
	lon = ds.coords['lon']
	adjusted_lon = ((lon + 180) % 360) - 180

	ds = ds.assign_coords(lon=adjusted_lon)
	ds = ds.sortby(['lat', 'lon'], ascending=True)

	return ds

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
