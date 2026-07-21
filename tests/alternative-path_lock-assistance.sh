if [ -z src/ ]; then
	echo "Error: src/ not found; run this script from the root directory."
	exit 1
fi


USER="USER-001"
VEHICLE="V-01"
STATION="STATION-bologna-02"
STATION_START_PORT="5001"
STATION_END_PORT="5002"
RIDE_TIME="10"


curl localhost/db
curl localhost:${STATION_START_PORT}/station
echo
curl localhost:${STATION_END_PORT}/station
sleep 2
# wait after each call for DB update


echo
python src/user/user.py scan ${USER} ${VEHICLE}
sleep 2
# Expected output:
# Success
curl localhost/db
curl localhost:${STATION_START_PORT}/station
# Expected output:
# no V-01


sleep $RIDE_TIME
# wait for a few loops of vehicle updates to FleetManagement


echo
python src/user/user.py lock ${USER} ${VEHICLE} ${STATION}
sleep 2
# Expected output:
# Success
# Some error (in docker logs): won't have locked nor parked
curl localhost/db
curl localhost:${STATION_END_PORT}/station


echo
python src/user/user.py lock_assistance ${USER} ${VEHICLE} ${STATION}
sleep 2
# Expected output:
# Success
# Expected output:
# the process duplicates: one sub-process goes to manual assistance,
# the other proceeds normally to the payment
curl localhost/db
curl localhost:${STATION_END_PORT}/station

