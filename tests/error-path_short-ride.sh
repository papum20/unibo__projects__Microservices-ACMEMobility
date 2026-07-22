# When a ride is too short, no data will have been transmitted from vehicle to FleetManagement,
# so ACME won't be able to fetch any position or battery data.


if [ -z src/ ]; then
	echo "Error: src/ not found; run this script from the root directory."
	exit 1
fi


USER="USER-001"
VEHICLE="V-01"
STATION="STATION-bologna-02"
STATION_START_PORT="5001"
STATION_END_PORT="5002"
RIDE_TIME="0"


curl localhost/db
curl localhost:${STATION_START_PORT}/station
echo
curl localhost:${STATION_END_PORT}/station
sleep 3
# wait after each call for DB update


echo
python src/user/user.py scan ${USER} ${VEHICLE}
sleep 1
# Expected output:
# Success


sleep $RIDE_TIME


echo
python src/user/user.py park ${USER} ${VEHICLE} ${STATION}
sleep 3
# Expected output:
# Success
curl localhost/db
curl localhost:${STATION_END_PORT}/station


echo
python src/user/user.py lock ${USER} ${VEHICLE} ${STATION}
sleep 3
# Expected output:
# Success
curl localhost/db
curl localhost:${STATION_END_PORT}/station

# Check docker logs: error from ACME fetching battery
# Check Camunda cockpit: process gone to the manual error task
