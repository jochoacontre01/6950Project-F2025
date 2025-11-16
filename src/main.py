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
			year = np.arange(2015, 2051, dtype=int)
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