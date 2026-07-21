if [ -z src/ ]; then
	echo "Error: src/ not found; run this script from the root directory."
	exit 1
fi


USER="USER-001"
VEHICLE="V-01"
STATION="STATION-bologna-02"
STATION_START_PORT="5001"
STATION_END_PORT="5002"


curl localhost/db
# Expected output:
# V-01 locked in STATION-bologna-01
# USER-001 has no vehicle
curl localhost:${STATION_START_PORT}/station
# Expected output:
# V-01 locked
echo
curl localhost:${STATION_END_PORT}/station
# Expected output:
# no V-01
sleep 2
# wait after each call for DB update


echo
python src/user/user.py reserve ${USER} ${VEHICLE}
sleep 3
# Expected output:
# Success
curl localhost/db
# Expected output:
# USER-001 has reserved V-01

echo
python src/user/user.py cancel ${USER} ${VEHICLE}
sleep 2
# Expected output:
# Success
curl localhost/db
# Expected output:
# db reset like before reservation
curl localhost:${STATION_START_PORT}/station
