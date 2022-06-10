from smarthome.constants import EnergySource as sources
from smarthome.models import EnergySurplusRaport

storage_home_setups_list = [
#     {   # TODO - nie działa ładowanie akumulatora :c 
#         # There are no photovoltaics, no stored energy, 
#         # but surplus energy is enough to power every device and to chatge energy storage
#         "storage_capacity": 6,
#         "storage_voltage": 24, # 0.0144 w godzinę
#         "initial_grid_surplus_value": 10, # 8 do wykorzystania
#         "initial_storage_charge_value": 2,
#         "first_window": {
#             "receiver_energy": 5,
#             "generator_energy": 0,
#             "sources": {
#                 "photovoltaics_used": 0,
#                 "grid_surplus_used": 5.0144,
#                 "energy_storage_used": 0,
#                 "public_grid_used": 0, 
#             },
#             "surpluses": {
#                 sources.GRID_SURPLUS : {
#                     "usage_type": EnergySurplusRaport.DEVICES_POWERING,
#                     "surplus_total_value": 2.9856,
#                     "surplus_iteration_value_transfered": 0,
#                 },
#                 sources.ENERGY_STORAGE : {
#                     "iteration_energy_stored": 0.0144,
#                     "total_energy_in_storage": 2.0144,
#                 }
#             }
#         }
#     },
#     { 
#         "storage_capacity": 6,
#         "storage_voltage": 24,
#         "initial_grid_surplus_value": 10,
#         "initial_storage_charge_value": 0,
#         "first_window": {
#             "receiver_energy": 0,
#             "generator_energy": 0,
#             "sources": {
#                 "photovoltaics_used": 0,
#                 "grid_surplus_used": 0.0144,
#                 "energy_storage_used": 0,
#                 "public_grid_used": 0, 
#                 },
#             "surpluses": {
#                 sources.GRID_SURPLUS : {
#                     "usage_type": EnergySurplusRaport.DEVICES_POWERING,
#                     "surplus_total_value": 7.9856,
#                     "surplus_iteration_value_transfered": 0,
#                     },
#                 sources.ENERGY_STORAGE : {
#                     "iteration_energy_stored": 0.0144,
#                     "total_energy_in_storage": 0.0144,
#                 }

#             }
#         }
#     }
]  
