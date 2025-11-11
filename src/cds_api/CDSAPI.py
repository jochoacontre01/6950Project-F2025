
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
    
