from enum import Enum
from get_env import get_env_or_exit



class User:
	def __init__(self, user_id, username, saved_card):
		self.user_id	= user_id
		self.username	= username
		self.saved_card	= saved_card

class Vehicle:

	class Status(Enum):
		AVAILABLE	= 1
		CHARGING	= 2
		MAINTENANCE	= 3
		RENTED		= 4
		RESERVED	= 5

	def __init__(self, vehicle_id, status, reserved_by, rented_by, current_station):
		self.vehicle_id			= vehicle_id
		self.status				= status
		self.reserved_by		= reserved_by
		self.rented_by			= rented_by
		self.current_station 	= current_station


class DataBase:


	# Simulated ACME Core Database (Users)
	acme_user_db = {}

	# Simulated ACME Core Database (Inventory & State)
	acme_vehicle_db = {}

	def __init__(self):

		users = [
			get_env_or_exit('USER_ID_01'),
			get_env_or_exit('USER_ID_02'),
			get_env_or_exit('USER_ID_03'),
			get_env_or_exit('USER_ID_04'),
			get_env_or_exit('USER_ID_05')
		]
		user_names = [
			get_env_or_exit('USER_01_NAME'),
			get_env_or_exit('USER_02_NAME'),
			get_env_or_exit('USER_03_NAME'),
			get_env_or_exit('USER_04_NAME'),
			get_env_or_exit('USER_05_NAME')
		]
		user_cards = [
			get_env_or_exit('USER_01_CARD'),
			get_env_or_exit('USER_02_CARD'),
			get_env_or_exit('USER_03_CARD'),
			get_env_or_exit('USER_04_CARD'),
			get_env_or_exit('USER_05_CARD')
		]

		vehicles = [
			get_env_or_exit('VEHICLE_ID_01'),
			get_env_or_exit('VEHICLE_ID_02'),
			get_env_or_exit('VEHICLE_ID_03'),
			get_env_or_exit('VEHICLE_ID_04'),
			get_env_or_exit('VEHICLE_ID_05'),
			get_env_or_exit('VEHICLE_ID_06'),
			get_env_or_exit('VEHICLE_ID_07'),
			get_env_or_exit('VEHICLE_ID_08'),
			get_env_or_exit('VEHICLE_ID_09'),
			get_env_or_exit('VEHICLE_ID_10')
		]
		vehicle_stations = [
			get_env_or_exit('VEHICLE_01_START_STATION'),
			get_env_or_exit('VEHICLE_02_START_STATION'),
			get_env_or_exit('VEHICLE_03_START_STATION'),
			get_env_or_exit('VEHICLE_04_START_STATION'),
			get_env_or_exit('VEHICLE_05_START_STATION'),
			get_env_or_exit('VEHICLE_06_START_STATION'),
			get_env_or_exit('VEHICLE_07_START_STATION'),
			get_env_or_exit('VEHICLE_08_START_STATION'),
			get_env_or_exit('VEHICLE_09_START_STATION'),
			get_env_or_exit('VEHICLE_10_START_STATION')
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
				vehicle_stations[idx]
			)
	

	def get_user(self, user_id) -> User | None:
		"""Simulate fetching the user's saved card from a database or external service."""
		return self.acme_user_db.get(user_id, None)

	def get_vehicle(self, vehicle_id) -> Vehicle | None:
		"""Simulate fetching the vehicle's status from a database or external service."""
		return self.acme_vehicle_db.get(vehicle_id, None)


	def update_vehicle(self, vehicle: Vehicle) -> bool:
		"""Simulate updating the vehicle's status in a database or external service."""
		if vehicle.vehicle_id in self.acme_vehicle_db:
			self.acme_vehicle_db[vehicle.vehicle_id].status				= vehicle.status
			self.acme_vehicle_db[vehicle.vehicle_id].reserved_by		= vehicle.reserved_by
			self.acme_vehicle_db[vehicle.vehicle_id].rented_by			= vehicle.rented_by
			self.acme_vehicle_db[vehicle.vehicle_id].current_station	= vehicle.current_station
			return True
		return False


DATABASE = DataBase()
