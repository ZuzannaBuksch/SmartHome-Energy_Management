from typing import Tuple
from functools import wraps

def is_energy_needed(func):
        @wraps(func)
        def wrap(self, energy_demand, *args, **kwargs):
            is_energy_needed = energy_demand<0
            if is_energy_needed:
                return func(self, energy_demand, *args, **kwargs)
            return (0,energy_demand)
        return wrap

class BaseEnergyCalculator:
    slug = None

    def __init__(self, building):
            self._building=building
    
    def calculate_energy_cover(self, energy_demand: float) -> Tuple[float, float]:
        raise NotImplementedError

