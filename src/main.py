from cds_api.CDSAPI import CDSExtract
import numpy as np


client = CDSExtract(
	temporal_resolution='daily',
	experiment='SSP3-7.0',
	variable='Near-surface air temperature',
	model='CESM2 (USA)',
	year=np.arange(2015, 2051, dtype=int),
	month=np.arange(1, 13, dtype=int),
	day=np.arange(1, 31, dtype=int)
)

client.retrieve_request()