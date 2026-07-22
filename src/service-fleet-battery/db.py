

class Vehicle:

	def __init__(self, vehicle_id: str, battery_perc: float, time_epoch_s: float):
		self.vehicle_id		= vehicle_id
		self.battery_perc	= battery_perc
		self.time_epoch_s	= time_epoch_s

	def to_dict(self):
		return {
			"vehicleId": self.vehicle_id,
			"battery": self.battery_perc,
			"timestamp": self.time_epoch_s
		}


class DataBase:

	# Simulated Database
	vehicle_db = {
		
	}

	def get_vehicle(self, vehicle_id) -> Vehicle | None:
		"""Simulate fetching the vehicle's status from a database or external service."""
		return self.vehicle_db.get(vehicle_id, None)


	def get_all_vehicles(self) -> list[Vehicle]:
		"""Simulate fetching all vehicles from a database or external service."""
		return list(self.vehicle_db.values())


	def add_vehicle(self, vehicle_id: str) -> Vehicle:
		"""Add a new vehicle to the database."""
		if vehicle_id not in self.vehicle_db:
			new_vehicle = Vehicle(vehicle_id, battery_perc=100.0, time_epoch_s=0.0)
			self.vehicle_db[vehicle_id] = new_vehicle
			return new_vehicle
		else:
			return self.vehicle_db[vehicle_id]


	def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
		"""Simulate creating or updating a vehicle in the database."""
		if vehicle.vehicle_id not in self.vehicle_db:
			self.vehicle_db[vehicle.vehicle_id] = vehicle
			return self.vehicle_db[vehicle.vehicle_id]
		else:
			return self.vehicle_db[vehicle.vehicle_id]


DATABASE = DataBase()
