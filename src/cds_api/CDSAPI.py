import os
from warnings import warn

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


    def retrieve_request(self, target_directory=None, overwrite_duplicated=False):
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
                'day': [str(d) for da in self.day] if self.day is not None else None,
            }.items()
            if value is not None
        }

        print(f'Retrieving {self.target}')

    
