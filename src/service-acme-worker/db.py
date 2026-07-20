import logging
from enum import Enum
from get_env import get_env_or_exit

logger = logging.getLogger(__name__)


class User:
	def __init__(self, user_id, username, saved_card):
		self.user_id	= user_id
		self.username	= username
		self.saved_card	= saved_card
		
	def __repr__(self):
		return f"<User id='{self.user_id}' name='{self.username}' card='{self.saved_card}'>"

	def to_dict(self):
		return {
			"user_id": self.user_id,
			"username": self.username,
			"saved_card": self.saved_card
		}


class Vehicle:

	vehicle_id		: str
	status			: Enum
	reserved_by		: str | None
	rented_by		: str | None
	current_station	: str | None
	battery_perc	: int

	class Status(Enum):
		AVAILABLE	= "available"
		RESERVED	= "reserved"
		RENTED		= "rented"
		MAINTENANCE	= "maintenance"
		CHARGING	= "charging"

	def __init__(self, vehicle_id, status, reserved_by, rented_by, current_station, battery_perc):
		self.vehicle_id			= vehicle_id
		self.status				= status
		self.reserved_by		= reserved_by
		self.rented_by			= rented_by
		self.current_station 	= current_station
		self.battery_perc		= battery_perc
		
	def __repr__(self):
		return (f"<Vehicle id='{self.vehicle_id}' status='{self.status.value}' "
				f"station='{self.current_station}' battery={self.battery_perc}% "
				f"reserved_by='{self.reserved_by}' rented_by='{self.rented_by}'>")

	def to_dict(self):
		return {
			"vehicle_id": self.vehicle_id,
			"status": self.status.value,  # Extract the string value of the Enum
			"reserved_by": self.reserved_by,
			"rented_by": self.rented_by,
			"current_station": self.current_station,
			"battery_perc": self.battery_perc
		}



class DataBase:


	# Simulated ACME Core Database (Users)
	acme_user_db = {}

	# Simulated ACME Core Database (Inventory & State)
	acme_vehicle_db = {}

	def __init__(self):

		USER_N			= get_env_or_exit('USER_N')
		USER_DIGITS		= get_env_or_exit('USER_DIGITS')
		VEHICLE_N		= get_env_or_exit('VEHICLE_N')
		VEHICLE_DIGITS	= get_env_or_exit('VEHICLE_DIGITS')

		users = [
			get_env_or_exit(f'USER_ID_{str(i+1).zfill(int(USER_DIGITS))}') for i in range(int(USER_N))
		]
		user_names = [
			get_env_or_exit(f'USER_{str(i+1).zfill(int(USER_DIGITS))}_NAME') for i in range(int(USER_N))
		]
		user_cards = [
			get_env_or_exit(f'USER_{str(i+1).zfill(int(USER_DIGITS))}_CARD') for i in range(int(USER_N))
		]

		vehicles = [
			get_env_or_exit(f'VEHICLE_ID_{str(i+1).zfill(int(VEHICLE_DIGITS))}') for i in range(int(VEHICLE_N))
		]
		vehicle_stations = [
			get_env_or_exit(f'VEHICLE_{str(i+1).zfill(int(VEHICLE_DIGITS))}_START_STATION') for i in range(int(VEHICLE_N))
		]

		for idx, user_id in enumerate(users):
			self.acme_user_db[user_id] = User(
				user_id,
				user_names[idx],
				user_cards[idx]
			)

		for idx, vehicle_id in enumerate(vehicles):
			self.acme_vehicle_db[vehicle_id] = Vehicle(
				vehicle_id,
				Vehicle.Status.AVAILABLE,
				None,
				None,
				vehicle_stations[idx],
				100
			)
		
		logger.info("Initialized ACME Database. Users: %s; Vehicles: %s", self.acme_user_db, self.acme_vehicle_db)
	

	def get_user(self, user_id) -> User | None:
		"""Simulate fetching the user's saved card from a database or external service."""
		return self.acme_user_db.get(user_id, None)

	def get_vehicle(self, vehicle_id) -> Vehicle | None:
		"""Simulate fetching the vehicle's status from a database or external service."""
		return self.acme_vehicle_db.get(vehicle_id, None)

	def get_all_users(self) -> list[User]:
		"""Simulate fetching all users from a database or external service."""
		return list(self.acme_user_db.values())
	
	def get_all_vehicles(self) -> list[Vehicle]:
		"""Simulate fetching all vehicles from a database or external service."""
		return list(self.acme_vehicle_db.values())


	def update_vehicle(self, vehicle: Vehicle) -> bool:
		"""Simulate updating the vehicle's status in a database or external service."""
		if vehicle.vehicle_id in self.acme_vehicle_db:
			self.acme_vehicle_db[vehicle.vehicle_id].status				= vehicle.status
			self.acme_vehicle_db[vehicle.vehicle_id].reserved_by		= vehicle.reserved_by
			self.acme_vehicle_db[vehicle.vehicle_id].rented_by			= vehicle.rented_by
			self.acme_vehicle_db[vehicle.vehicle_id].current_station	= vehicle.current_station
			self.acme_vehicle_db[vehicle.vehicle_id].battery_perc		= vehicle.battery_perc
			return True
		return False


DATABASE = DataBase()
