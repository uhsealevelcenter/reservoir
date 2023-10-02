#!/bin/sh

### ACTIVATE VIRTUAL ENV. ###
. /home/samw/venv/venv/bin/activate

### PROCESS HOME DIRECTORY. ###
PROCESS_HOME="/home/nwstg/reservoir"

### EXECUTE RESERVOIR CSV RECREATION FOR SINGLE STATION. ###
#python3 ${PROCESS_HOME}/recreate_reservoir_csvs.py --station_id=EDD0C70A

### EXECUTE RESERVOIR CSV RECREATION FOR ALL STATIONS. ###
python3 ${PROCESS_HOME}/recreate_reservoir_csvs.py
