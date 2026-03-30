from enum import Enum



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
	acme_user_db = {
		"u001": User(
			"u001",
			"Alice",
			"1111-1111"
		),
		"u002": User(
			"u002",
			"Bob",
			"1111-1112"
		)
	}

	# Simulated ACME Core Database (Inventory & State)
	acme_vehicle_db = {
		"v001": Vehicle(
			"v001",
			Vehicle.Status.AVAILABLE,
			None,
			None,
			"s001"
		),
		"v002": Vehicle(
			"v002",
			Vehicle.Status.AVAILABLE,
			None,
			None,
			"s002"
		)
	}

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
