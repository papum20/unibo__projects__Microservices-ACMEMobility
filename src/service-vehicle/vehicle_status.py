from enum import Enum

class VehicleStatus(Enum):
	STOPPED	= "stopped"	# off, not used
	MOVING	= "moving"	# on and moving
	HALTED	= "halted"	# on but not moving (e.g. at a traffic light)
