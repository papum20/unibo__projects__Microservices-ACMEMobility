# Microservices-ACMEMobility
Project for the Microservice Architecture course at University of Bologna 2025/2026. ACMEMobility: vehicle renting and sharing service.

## Requirements

- docker
- Java Runtime Environment 17


## Notes

http://localhost:8080/camunda/app/cockpit/  
Login: demo / demo  


## Commands

Execute all commands from inside the `src/` directory:
```bash
cd src/
```

Start all services:
```bash
./start.sh
```

Stop all services:
```bash
docker compose down
```

Launch commands as user:
```bash
python3 user-scripts/user.py scan u001 v001
python3 user-scripts/user.py reserve u001 v001
python3 user-scripts/user.py scan_reserved u001 v001
python3 user-scripts/user.py cancel u001 v001
python3 user-scripts/user.py park u001 v001 s001
```
