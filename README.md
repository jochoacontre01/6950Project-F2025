
# **IPCC climte scenarios: how our decisions are shaping our future**
Project for the course "6950 - Computer based tools and applications" during Fall 2025 semester, Memorial University of Newfoundland

## Objective

Analyze the changes in temperature and its relationship with snow depth in Newfoundland, Canada, under historical changes and different climatic outcomes, such as the climate scenarios SSP2-4.5 and SSP3-7.0

## Methodology

Using the open data from the CMIP6, part of the Intergovernmental Panel on Climate Change (IPCC) efforts to provide meaningful climate data, we analyze how the global temperatures relate to the snow depth on susceptible areas, such as the coasts of Newfoundland and atlantic Canada.

The project consists on analyzing gridded data for multiple variables and timelines (from 1950 to 2050), using data analysis and libraries such as `xarray`, `numpy`, as well as API calls and file management.

## Expected results

Timeline of changes of temperature and snow depth to compare what are the possible outcomes given our current political and environmental decisions, as well as maps to show regional changes and affected areas in more detail.

---

 - You can check the open data in [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/datasets/projections-cmip6?tab=overview).
 - The IPCC is the Intergovernmental Panel on Climate Change, part of the United Nations, dedicated to environmental research for policy makers. The IPCC only compiles the most recent scientific concensus on climate change and does not make their own research.
 - The CMIP6 is the Coupled Model Intercomparison Project Phase 6, a project of the World Climate Research Programme providing climate projections to understand past, present and future climate changes.

## How to reproduce the project

In order to reproduce the figures in this project, you must first install and setup an API call from the Climate Data Store following [the instructions](https://cds.climate.copernicus.eu/how-to-api). 

1. Once you have your API key set up and running, run the following code to download the data:

```python

from cds_api.CDSAPI import CDSExtract
import numpy as np

experiments = ['Historical','SSP2-4.5','SSP3-7.0']
variables = [
	'Near-surface air temperature',
	'Snow depth'
]

for experiment in experiments:
	for variable in variables:
		if experiment != 'Historical':
			year = np.arange(2015, 2101, dtype=int)
		else:
			year = np.arange(1950, 2016, dtype=int)

		client = CDSExtract(
			temporal_resolution='monthly',
			experiment=experiment,
			variable=variable,
			model='CESM2 (USA)',
			year=year,
			month=np.arange(1, 13, dtype=int)
		)

		client.retrieve_request(overwrite_duplicated=False)
		client.unzip(overwrite=False)

```

In this code you can input custom parameters as per your specific requirements, but the ones set by default will give the exact same results as the ones in this project. This code can be found in the file `main.py`. The files will download by default in a new folder called data in the parent directory.

2. Download the world administrative boundaries shapefile from the [recommended database](https://public.opendatasoft.com/explore/assets/world-administrative-boundaries/) and save the extracted folder to a directory named `assets` in the parent directory.
   
3. Locate the script `plot.py` and run it. Be sure to load the correct files in the lines 36, 50 and 62, changing by the relative path of the NC file you wish to plot. The variables are set up to accept a historical file and two future scenarios. 

4. Additionally, in the lines 143, 155, 167 be sure to change `temp` by `snow` and viceversa according to your current dataset. This does not affect the figure creations, but it might be good to save them with a meaningful name.

