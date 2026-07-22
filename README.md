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


## Usage

Web pages:  
*	Camunda cockpit: http://localhost:8080/camunda/app/cockpit/  
	*	Login: demo / demo  
*	GraphHopper routing service: http://localhost:8989/  
*	FleetManagement map visualizer: http://localhost:4000/map/  


### Commands

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
python3 src/user/user.py lock_assistance USER-001 V-01
python3 src/user/user.py steal USER-001 V-01
python3 src/user/user.py force_timeout USER-001 V-01
```

In `tests/` there are some bash scripts to test the system with different scenarios. They can used as an example, or launched directly, for example:
```bash
# after the system has been launched with ./src/start.sh
# and has fully started
./tests/test_happy_path.sh
```

#### Debugging

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

Fetch a vehicle's info:
```bash
curl localhost:6011/status
curl localhost:6012/status
curl localhost:6013/status
curl localhost:6014/status
curl localhost:6015/status
curl localhost:6016/status
curl localhost:6017/status
curl localhost:6018/status
curl localhost:6019/status
curl localhost:6020/status
```

Fetch FleetManagement databases:  
```bash
curl localhost:4000/tracking/position/V-01
curl localhost:4000/tracking/position/V-01/history
curl localhost:4000/tracking/position/active
curl localhost:4000/tracking/position/all
curl localhost:4000/tracking/battery/V-01
curl localhost:4000/tracking/battery/all
```


### Configuration

All variables are in the `src/.env` file.  
The infrastructure is in the `docker-compose.template.yml` file.  
These files are then converted into the final ones for execution by the `src/bash-utils/compile-dockercompose.sh` script, also called by `./src/start.sh`.  

Camunda uses a debugging diagram (`src/camunda-resources-debug/diagram-collaboration-camunda-debug.bpmn`), with additional user tasks before all end tasks, to stop the processes for manual inspection; the final diagram (`src/camunda-resources-debug/diagram-collaboration-camunda-debug.bpmn`) can be switched from `docker-compose.template.yml`, changing the volume path for the `camunda` service.  


## Documentation

*	`docs/paper/main.pdf`: the report of the project (in italian)
*	`docs/diagrams/diagram-SOA.uml`: SOA diagram in UML (TinySOA) (to paste in https://www.planttext.com/)  
*	`docs/diagrams/formal-choreography.md`: formal choreography of the system, in textual form  
*	`docs/diagrams/diagram-collaboration-full.bpmn`: full BPMN collaboration diagram (for documentation, with all participants defined)
	*	`docs/diagrams/diagram-collaboration-full.pdf`: image


## Refs

*	leaflet javascript library: https://leafletjs.com/  
*	GraphHopper routing service - web API usage: https://docs.graphhopper.com/openapi/getroute  
