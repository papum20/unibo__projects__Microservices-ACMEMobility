if [ -z src/ ]; then
	echo "Error: src/ not found; run this script from the root directory."
	exit 1
fi


USER="USER-001"
VEHICLE="V-01"
STATION="STATION-bologna-02"
STATION_START_PORT="5001"
STATION_END_PORT="5002"


echo "Remember to first set CAMUNDA_PENALTY_CANCELLATION_MINUTES=PT10S"
read -p "Press Enter to continue (or Ctrl+C to cancel)..."


curl localhost/db
sleep 2
# wait after each call for DB update


echo
python src/user/user.py reserve ${USER} ${VEHICLE}
sleep 3
# Expected output:
# Success
curl localhost/db
# db reset like before reservation
