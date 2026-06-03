from enum import Enum

class VehicleStatus(Enum):
	STOPPED	= 0	# off, not used
	MOVING	= 1 # on and moving
	HALTED	= 2 # on but not moving (e.g. at a traffic light)
