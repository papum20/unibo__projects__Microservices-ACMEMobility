# Microservices-ACMEMobility
Project for the Microservice Architecture course at University of Bologna 2025/2026. ACMEMobility: vehicle renting and sharing service.

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

http://localhost:8080/camunda/app/cockpit/  
Login: demo / demo  


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
python3 src/user/user.py scan u001 v001
python3 src/user/user.py reserve u001 v001
python3 src/user/user.py scan_reserved u001 v001
python3 src/user/user.py cancel u001 v001
python3 src/user/user.py park u001 v001 s001
```

## Diagrams

`docs/diagrams/diagram-SOA.uml`: SOA diagram in UML (TinySOA) (to paste in https://www.planttext.com/)  
