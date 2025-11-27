import pytest
import xarray as xr
import numpy as np
import pandas as pd
from extreme_events import higher_than_average

def synthetic_dataset(start_year, end_year, values):
    """Creates dummy data

    Args:
        start_year (int): Starting year
        end_year (int): Ending year
        values (list): List of values to distribute along the array

    Returns:
        xr.DataArray: Simulated data
    """    
    times = pd.date_range(
        start=f'{start_year}-01-01',
        end=f'{end_year}-01-01',
        freq="ME"
    )
    
    lats = np.arange(50, 56, 1, dtype=float)
    lons = np.arange(-40, -34, 1, dtype=float)
    
    data = np.ones((len(times), len(lats), len(lons)), dtype=float)
    if len(values) == 1:
        data *= values
    else:
        blocks = len(values)
        block_data_len = int(len(times) / blocks)
        for i, _ in enumerate(range(blocks)):
            data[block_data_len*i:block_data_len*(i+1)] = values[i]
    
    da = xr.DataArray(
        data,
        coords={
            "time": times,
            "lat": lats,
            "lon": lons
        },
        dims=(
            "time", "lat", "lon"
        ),
        name="tas"
    )
            
    return da

    
base_1 = synthetic_dataset(1990, 1995, [2,3,6,1,3])
control_1 = synthetic_dataset(2015, 2020, [4,6,4,7,6])

base_2 = synthetic_dataset(1990, 1995, [2,3,6,1,3])
control_2 = synthetic_dataset(2015, 2020, [4,6,4,5,5])

base_3 = synthetic_dataset(1990, 1995, [2,3,6,1,3])
control_3 = synthetic_dataset(2015, 2020, [4,7,5,7,6])


@pytest.mark.parametrize('base_temp_grid,objective_temp_grid,expected',[
    # Regular case, one match
    (base_1, control_1, 2018),
    # Case where there is no match
    (base_2, control_2, None),
    # Case with multiple matches (the function catches the first match)
    (base_3, control_3, 2016),
])
def test_higher(base_temp_grid, objective_temp_grid, expected):
    assert higher_than_average(base_temp_grid, objective_temp_grid) == expected
