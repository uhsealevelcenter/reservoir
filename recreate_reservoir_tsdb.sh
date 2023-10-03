#!/bin/sh

### ACTIVATE VIRTUAL ENV. ###
. /home/samw/venv/venv/bin/activate

### PROCESS HOME DIRECTORY. ###
PROCESS_HOME="/home/nwstg/reservoir"

### DIRECTORY CONTAINING FULL PRODUCTION CSV FILES. ###
CSV_DIR="/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"

### LIST OF ALL FULL CSV FILES. ###
FULL_CSV_FILES=`ls -1 ${CSV_DIR}/*full.csv`

### MAKE TEMPORARY OUTPUT DIRECTORY IF IT DOES NOT EXIST. ###
if [ ! -e "${CSV_DIR}/tsdb" ]; then
  mkdir ${CSV_DIR}/tsdb
fi

### LOOP THROUGH AND CREATE NEW CSV FILES IN A TEMPORARY DIRECTORY WITH A FORMAT ###
### IDEAL FOR TIMESCALE DB. ###
for FULL_CSV_FILE in $FULL_CSV_FILES
do

  ### CSV FILENAME AND STATION ID.
  CSV_FILENAME=`echo "${FULL_CSV_FILE}" | xargs -n 1 basename`
  STATION_ID=`echo "${CSV_FILENAME}" | cut -d'-' -f1`

  ### SEPARATE STATIONS INTO THEIR OWN CSV FILES. ###
  awk -v stid=${STATION_ID} -F',' '{ print stid","$1","$2","$3","$4 }' ${FULL_CSV_FILE} > ${CSV_DIR}/tsdb/${STATION_ID}-tsdb.csv

  ### REFORMAT TIME COLUMN. ###
  sed -i "s/T/ /g" ${CSV_DIR}/tsdb/${STATION_ID}-tsdb.csv
  sed -i "s/Z/+00:00/g" ${CSV_DIR}/tsdb/${STATION_ID}-tsdb.csv

  ### UPDATE HEADER. ###
  sed -i "s/${STATION_ID},date,data,bv,txtype/reservoir_id,time,water_level,battery_voltage,data_type/g" ${CSV_DIR}/tsdb/${STATION_ID}-tsdb.csv

done

### TRUNCATE AND UPDATE RESERVOIR DATABASE TABLE WITH LATEST CSV DATA. ### 
python3 ${PROCESS_HOME}/recreate_reservoir_tsdb.py
