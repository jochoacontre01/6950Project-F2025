import os
from warnings import warn
import cdsapi 
import time
from requests.exceptions import ChunkedEncodingError

class CDSExtract:


    def __init__(self,
        temporal_resolution:str=None,
        experiment:str=None,
        variable:str=None,
        model:str=None,
        year:list=None,
        month:list=None,
        day:list=None,
        level:list=None,
        ):
        
        self.temporal_resolution = temporal_resolution
        self.experiment = experiment
        self.variable = variable
        self.model = model
        self.year = year
        self.month = month
        self.day = day
        self.level = level

        if self.year is not None:
            self.target = f'{self.variable}_{self.temporal_resolution.lower()}_{self.experiment}_{self.model}_{min(self.year)}-{max(self.year)}.zip'
        else:
            self.target = f'{self.variable}_{self.temporal_resolution.lower()}_{self.experiment}_{self.model}.zip'


    def retrieve_request(self, target_directory=None, overwrite_duplicated=False, retries=5, timeout_duration=5):
        if target_directory is None:
            target_directory = os.getcwd()

        os.makedirs(target_directory, exist_ok=True)

        self.full_target_file = os.path.join(target_directory, self.target)

        if os.path.exists(self.full_target_file):
            if overwrite_duplicated:
                warn(f'Overwriting existing file: {self.full_target_file}', category=Warning)
                os.remove(self.full_target_file)
            else:
                warn('This dataset already exists! Skipping API call.', category=Warning)
                return
        
        dataset = 'projections-cmip6'
        request = {
            key: value
            for key, value in {
                'temporal_resolution': self.temporal_resolution.lower(),
                'experiment': self.experiment,
                'variable': self.variable,
                'level': self.level,
                'model': self.model,
                'year': [str(y) for y in self.year] if self.year is not None else None,
                'month': [str(m) for m in self.month] if self.month is not None else None,
                'day': [str(d) for d in self.day] if self.day is not None else None,
            }.items()
            if value is not None
        }

        print(f'Retrieving {self.target}')

        client = cdsapi.Client()
        retry_count = 0
        while retry_count < retries:
            try:
                client.retrieve(dataset, request, target=self.full_target_file)
                print(f'Successfully retrieved and saved to {self.full_target_file}')
                break
            except ChunkedEncodingError:
                retry_count += 1
                if retry_count < retries:
                    warn(f'ChunkedEncodingError encountered, perhaps a network error? Retrying {retry_count}/{retries}...', category=Warning)
                    time.sleep(timeout_duration)
                else:
                    warn('Max retries reached. Finishing execution', category=Warning)
