import xarray as xr
import numpy as np
from Process.GeometricProcessing import load_preprocess
import os



def higher_than_average(base_temp_grid, objective_temp_grid):
    """
        What is the first year whose average temperature is equal or higher than the historical records maximum?
        1. Compute the maximum for historical records
        2. Compute the average for each future year
        3. If a year's maximum value is higher than the maximum in the entire historical period, flag it
    """
    base_max = base_temp_grid.mean(dim=["lat","lon"]).max(dim="time")
    obj_yearly = objective_temp_grid.mean(dim=["lat","lon"]).resample(time="YE").max(dim="time")

    bigger_than_years = obj_yearly.where(obj_yearly > base_max, drop=True)

    if bigger_than_years.size > 0:
        return int(bigger_than_years.time.dt.year[0])
    else:
        return


interest_point = [55.37437902920724, -60.67567886857576]
buffer_deg = 15.0

ds_path_historical = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_historical_cesm2_1950-2015/tas_Amon_CESM2_historical_r1i1p1f1_gn_19500115-20141215.nc",
)

ds_path_245 = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_ssp2_4_5_cesm2_2015-2100/tas_Amon_CESM2_ssp245_r4i1p1f1_gn_20150115-21001215.nc",
)

ds_path_370 = os.path.join(
    os.path.dirname(__file__),
    "data/near_surface_air_temperature_monthly_ssp3_7_0_cesm2_2015-2100/tas_Amon_CESM2_ssp370_r4i1p1f1_gn_20150115-21001215.nc",
)
base = load_preprocess(
    ds_path_historical, center_point=interest_point, buffer=buffer_deg
).ds
obj_1 = load_preprocess(ds_path_245, center_point=interest_point, buffer=buffer_deg).ds
obj_2 = load_preprocess(ds_path_370, center_point=interest_point, buffer=buffer_deg).ds

result_1 = higher_than_average(
    base,
    obj_1,
)

result_2 = higher_than_average(
    base,
    obj_2,
)

print(f'Year for experiment SSP2-4.5: {result_1}')
print(f'Year for experiment SSP3-7.0: {result_2}')
