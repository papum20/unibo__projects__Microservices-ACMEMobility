

class Vehicle:

	def __init__(self, vehicle_id: str, battery_perc: float, time_epoch_s: float):
		self.vehicle_id		= vehicle_id
		self.battery_perc	= battery_perc
		self.time_epoch_s	= time_epoch_s


class DataBase:

	# Simulated Database
	acme_vehicle_db = {
		
	}

	def get_vehicle(self, vehicle_id) -> Vehicle | None:
		"""Simulate fetching the vehicle's status from a database or external service."""
		return self.acme_vehicle_db.get(vehicle_id, None)


	def get_all_vehicles(self) -> list[Vehicle]:
		"""Simulate fetching all vehicles from a database or external service."""
		return list(self.acme_vehicle_db.values())


	def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
		"""Simulate creating or updating a vehicle in the database."""
		if vehicle.vehicle_id not in self.acme_vehicle_db:
			self.acme_vehicle_db[vehicle.vehicle_id] = vehicle
			return self.acme_vehicle_db[vehicle.vehicle_id]
		else:
			return self.acme_vehicle_db[vehicle.vehicle_id]


DATABASE = DataBase()
