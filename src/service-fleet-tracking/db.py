from vehicle_status import VehicleStatus



class HistoryEntry:

	def __init__(self, latitude: float, longitude: float, speed_kmh: float, status: VehicleStatus, time_epoch_s: float):
		self.latitude		= latitude
		self.longitude		= longitude
		self.speed_kmh		= speed_kmh
		self.status			= status
		self.time_epoch_s	= time_epoch_s

	def to_dict(self):
		return {
			"latitude": self.latitude,
			"longitude": self.longitude,
			"speed_kmh": self.speed_kmh,
			"status": self.status.value if hasattr(self.status, 'value') else self.status,
			"time_epoch_s": self.time_epoch_s
		}


class Vehicle:

	def __init__(self, vehicle_id: str, is_tracked: bool, history: list[HistoryEntry]):
		self.vehicle_id			= vehicle_id
		self.is_tracked			= is_tracked
		self.history			= history

  # Property helper to easily grab the latest position from the history list
	@property
	def current(self) -> HistoryEntry | None:
		return self.history[-1] if self.history else None

	def to_dict(self):
		return {
			"vehicleId": self.vehicle_id,
			"isTracked": self.is_tracked,
			"history": [entry.to_dict() for entry in self.history]
		}



class DataBase:

	# Simulated Database
	acme_vehicle_db = {}

	def get_vehicle(self, vehicle_id) -> Vehicle | None:
		"""Simulate fetching the vehicle's status from a database or external service."""
		return self.acme_vehicle_db.get(vehicle_id, None)


	def get_all_vehicles(self) -> list[Vehicle]:
		"""Simulate fetching all vehicles from a database or external service."""
		return list(self.acme_vehicle_db.values())


	def add_vehicle(self, vehicle_id: str, is_tracked: bool = False) -> Vehicle:
		"""Simulate adding a new vehicle to the database."""
		if vehicle_id not in self.acme_vehicle_db:
			new_vehicle = Vehicle(vehicle_id, is_tracked, [])
			self.acme_vehicle_db[vehicle_id] = new_vehicle
			return new_vehicle
		else:
			return self.acme_vehicle_db[vehicle_id]
		

	def add_vehicle_position(self, vehicle_id: str, entry: HistoryEntry) -> Vehicle:
		"""Simulate adding a new position entry for a vehicle in the database."""
		vehicle = self.get_vehicle(vehicle_id)
		if vehicle is None:
			vehicle = self.add_vehicle(vehicle_id)
		
		vehicle.history.append(entry)
		return vehicle


	def set_vehicle_tracking(self, vehicle_id: str, is_tracked: bool) -> Vehicle:
		"""Set the tracking status of a vehicle in the database, or create a new one if not present."""
		vehicle = self.get_vehicle(vehicle_id)
		if vehicle is None:
			vehicle = self.add_vehicle(vehicle_id, is_tracked)
		else:
			vehicle.is_tracked = is_tracked
		
		return vehicle


	def update_vehicle_tracking(self, vehicle_id: str, is_tracked: bool) -> Vehicle:
		"""Simulate updating the tracking status of a vehicle in the database."""
		vehicle = self.get_vehicle(vehicle_id)
		if vehicle is None:
			vehicle = self.add_vehicle(vehicle_id, is_tracked)
		else:
			vehicle.is_tracked = is_tracked
		
		return vehicle


DATABASE = DataBase()
