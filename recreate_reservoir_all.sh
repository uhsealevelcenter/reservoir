#!/bin/sh

### ACTIVATE VIRTUAL ENV. ###
. /home/samw/venv/venv/bin/activate

### PROCESS HOME DIRECTORY. ###
PROCESS_HOME="/home/nwstg/reservoir"

### EXECUTE RESERVOIR CSV RECREATION FOR ALL STATIONS. ###
${PROCESS_HOME}/recreate_reservoir_csvs.sh

### EXECUTE RESERVOIR DB RECREATION FOR ALL STATIONS. ###
${PROCESS_HOME}/recreate_reservoir_tsdb.sh
