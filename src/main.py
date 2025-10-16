from cds_api.extract_data import CDSData, get_api_request, get_file_name
import os

request = get_api_request()

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(parent_dir, 'data')
out = os.path.join(data_dir, get_file_name())

cdsrequest = CDSData(*request)
cdsrequest.make_request(out, overwrite=False)

cdsrequest.unzip()