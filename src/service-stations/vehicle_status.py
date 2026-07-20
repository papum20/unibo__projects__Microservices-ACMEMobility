from enum import Enum

class VehicleStatus(Enum):
	LOCKED	= 0	# parked and locked
	PARKED	= 1 # inserted in the terminal, but not yet locked
