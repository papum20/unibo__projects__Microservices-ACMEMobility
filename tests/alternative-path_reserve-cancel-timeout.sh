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
sleep 2
# wait after each call for DB update


echo
python src/user/user.py reserve ${USER} ${VEHICLE}
sleep 3
# Expected output:
# Success
curl localhost/db

echo
python src/user/user.py force_timeout ${USER} ${VEHICLE}
sleep 3
# Expected output:
# Success
curl localhost/db
# Expected output:
# db reset like before reservation

# Check docker logs: we expect the bank converting the caution to payment
