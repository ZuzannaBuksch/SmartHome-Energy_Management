from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport


photovoltaics_only_home_setups_list = [
    {
        "first_window": {
            "receiver_energy": 5,
            "generator_energy": 0,
            "sources": {
                "photovoltaics_used": 0,
                "grid_surplus_used": 0,
                "public_grid_used": 5, 
                },
             "surpluses": {
                sources.GRID_SURPLUS: {
                    "surplus_total_value": 0,
                    "surplus_iteration_value_transfered": 0,
                    "energy_loss": 0,
                    "usage_type": EnergySurplusRaport.TRANSFER,
                    },
            }
        }
    },


]  
