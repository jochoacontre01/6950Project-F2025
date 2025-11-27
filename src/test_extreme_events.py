import pytest
import xarray as xr
import numpy as np
import pandas as pd
from extreme_events import higher_than_average


def synthetic_dataset(start_year, end_year, value):
    times = pd.date_range(
        start=f'{start_year}-01-01',
        end=f'{end_year}-01-01',
        freq="ME"
    )
    
    lats = np.arange(50,61,1, dtype=float)
    lons = np.arange(-40,-30,1, dtype=float)
    
    data = np.ones((len(times), len(lats), len(lons)), dtype=float) * value
    
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
    
synthetic_dataset(1950, 2000, 5)


@pytest.mark.parametrize([
    (2015, 2030)
])
