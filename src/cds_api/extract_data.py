import cdsapi
import os
# from warnings import warn
import zipfile
from warnings import warn

class CDSData:


    def __init__(self, dataset, request):
        self.dataset = dataset
        self.request = request
        self.out_file = None
        self.deprecate() 

    def deprecate():
        warn(
            'This class is deprecated and should not be used'
            'Please use CDSAPI instead',
            category=DeprecationWarning,
            stacklevel=2
        )

    
    def make_request(self, out=None, overwrite=False):
        if out is None:
            self.out_file = os.path.join(self._create_parent_folder(), get_file_name())
            # self._check_file_exists(self._create_parent_folder(), overwrite)
        else:
            self.out_file = out
            if os.path.exists(self.out_file):
                if not overwrite:
                    return
                else:
                    os.remove(self.out_file)
                    self.out_file = out
            
        
        client = cdsapi.Client()
        client.retrieve(self.dataset, self.request, target=self.out_file)

    def _create_parent_folder(self):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(parent_dir, 'data')
        return data_dir
    
    def unzip(self, target=None):
        if target is None:
            target = os.path.join(os.path.dirname(self.out_file), os.path.basename(self.out_file)).split('.')[0]
        
        try:
            with zipfile.ZipFile(self.out_file, 'r') as zip_ref:
                zip_ref.extractall(target)
        except FileNotFoundError:
            raise FileNotFoundError('Ensure the zip file is downloaded or check the file path!')
        except zipfile.BadZipFile:
            raise zipfile.BadZipFile('The file is not a valid ZIP file. It may have downloaded incompletely.')

def get_file_name():
    _, request = get_api_request()

    filename = request['temporal_resolution'] + '_' + request['experiment'] + '_' + request['variable'] + '_' + request['model'] + '_' + request['year'][0] +'-'+ request['year'][-1] + '_' + request['month'][0] +'-'+ request['month'][-1] + '.zip'

    return filename
    
def get_api_request():

    dataset = "projections-cmip6"
    request = {
        "temporal_resolution": "monthly",
        "experiment": "historical",
        "variable": "near_surface_air_temperature",
        "model": "cesm2",
        "year": [
            "1950", "1951", "1952",
            "1953", "1954", "1955",
            "1956", "1957", "1958",
            "1959", "1960", "1961",
            "1962", "1963", "1964",
            "1965", "1966", "1967",
            "1968", "1969", "1970",
            "1971", "1972", "1973",
            "1974", "1975", "1976",
            "1977", "1978", "1979",
            "1980", "1981", "1982",
            "1983", "1984", "1985",
            "1986", "1987", "1988",
            "1989", "1990", "1991",
            "1992", "1993", "1994",
            "1995", "1996", "1997",
            "1998", "1999", "2000",
            "2001", "2002", "2003",
            "2004", "2005", "2006",
            "2007", "2008", "2009",
            "2010", "2011", "2012",
            "2013", "2014"
        ],
        "month": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12"
        ]
    }
        
    return dataset, request
