if [ -z src/ ]; then
	echo "Error: src/ not found; run this script from the root directory."
	exit 1
fi


USER="USER-001"
VEHICLE="V-01"
STATION="STATION-bologna-02"
STATION_START_PORT="5001"
STATION_END_PORT="5002"
# enough to deplete battery (discharge 1%/s)
RIDE_TIME="90"


curl localhost/db
curl localhost:${STATION_START_PORT}/station
echo
curl localhost:${STATION_END_PORT}/station
sleep 3
# wait after each call for DB update


echo
python src/user/user.py scan ${USER} ${VEHICLE}
sleep 3
# Expected output:
# Success
curl localhost/db
curl localhost:${STATION_START_PORT}/station


sleep $RIDE_TIME
# wait for a few loops of vehicle updates to FleetManagement


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

# Check docker logs: we expect to see a message about penalty and the bank charging a 10% penalty