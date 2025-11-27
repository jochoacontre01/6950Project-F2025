import xarray as xr
import os
from Process.StringOps import match_scenario

def crop(ds, latmin, latmax, lonmin, lonmax):
	ds_cropped = ds.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
	return ds_cropped

def adjust_coords(ds):
	lon = ds.coords['lon']
	adjusted_lon = ((lon + 180) % 360) - 180

	ds = ds.assign_coords(lon=adjusted_lon)
	ds = ds.sortby(['lat', 'lon'], ascending=True)

	return ds

class load_preprocess: 
    
    def __init__(self, path, center_point, buffer=0):
        
        self.path = path
        self.var = os.path.basename(self.path).split("_")[0]
        
        scenario = match_scenario(path).format()
        self.scenario = scenario if scenario is not None else "Historical"
        self.bbox = [
            center_point[0] - buffer,
            center_point[0] + buffer,
            center_point[1] - buffer,
            center_point[1] + buffer,
        ]
        self.ds = None
        
        self.load()

    def load(self):
        # ! Load dataset with xarray and perform basic preprocessing
        ds = xr.load_dataset(self.path, engine="h5netcdf")[self.var]
        if self.var == "tas":
            ds = ds - 273.15
        ds = adjust_coords(ds)
        ds = crop(ds, *self.bbox)
        ds += 1e-15  # ? Add stability constant
        self.ds = ds
        return self.ds
