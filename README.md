# Microservices-ACMEMobility
Project for the Microservice Architecture course at University of bologna 2025/2026. ACMEMobility: vehicle renting and sharing service.

## Requirements

- docker
- Java Runtime Environment 17

### Data

For the GraphHopper routing service, we use the OpenStreetMap data for the north-eastern region of Italy.
1.	downloaded it from the following link:
	```
	https://download.geofabrik.de/europe/italy/nord-est-latest.osm.pbf
	```
2.	move it to the `service-graphhopper/data/` directory and rename it to `geofabrik_italy-nord-est-260517.osm.pbf`:

Or with a one-line bash command:
```bash
wget -O service-graphhopper/data/geofabrik_italy-nord-est-260517.osm.pbf https://download.geofabrik.de/europe/italy/nord-est-latest.osm.pbf
```


## Notes

Camunda cockpit: http://localhost:8080/camunda/app/cockpit/  
Login: demo / demo  

GraphHopper routing service: http://localhost:8989/  
FleetManagement map visualizer: http://localhost:4000/map/  


## Commands

Start all services:
```bash
./src/start.sh
```

Stop all services:
```bash
./src/down.sh
```

Launch commands as user:
```bash
python3 src/user/user.py scan USER-001 V-01
python3 src/user/user.py reserve USER-001 V-01
python3 src/user/user.py cancel USER-001 V-01
python3 src/user/user.py scan_reserved USER-001 V-01
python3 src/user/user.py park USER-001 V-01 STATION-bologna-01
python3 src/user/user.py lock USER-001 V-01 STATION-bologna-01
python3 src/user/user.py lock_assistance USER-001 V-01 STATION-bologna-01
python3 src/user/user.py steal USER-001 V-01
```

### Debugging

Fetch current ACME database:  
```bash
curl localhost/db
```

Fetch a station's info:
```bash
curl localhost:5001/station
curl localhost:5002/station
curl localhost:5003/station
curl localhost:5004/station
curl localhost:5005/station
```


## Diagrams

`docs/diagrams/diagram-SOA.uml`: SOA diagram in UML (TinySOA) (to paste in https://www.planttext.com/)  


## Refs
https://leafletjs.com/  
https://docs.graphhopper.com/openapi/getroute  
