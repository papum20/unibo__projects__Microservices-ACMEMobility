import logging
from flask import Flask, jsonify

from get_env import config
from db import DATABASE



app = Flask(__name__)
app.json.compact = False
logger = logging.getLogger(__name__)



@app.route('/db', methods=['GET'])
def get_db():
	
	users		= DATABASE.get_all_users()
	vehicles	= DATABASE.get_all_vehicles()

	return jsonify({
		"users"		: [user.to_dict() for user in users],
		"vehicles"	: [vehicle.to_dict() for vehicle in vehicles]
	}), 200



def run_server():
	app.run(host='0.0.0.0', port=config.PORT_ACME)

if __name__ == '__main__':
	run_server()