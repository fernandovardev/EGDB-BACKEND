@echo off
set CONTAINER_ID=02d944c2535c
set SCRIPT_PATH=/api/manage.py

echo Running update_data...
docker exec -it %CONTAINER_ID% python %SCRIPT_PATH% update_data

echo Running update_inventory...
docker exec -it %CONTAINER_ID% python %SCRIPT_PATH% update_inventory

echo Running manage_measures...
docker exec -it %CONTAINER_ID% python %SCRIPT_PATH% manage_measures

echo All commands executed.

