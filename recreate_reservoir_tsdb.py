import os
import psycopg2

import pandas as pd

from glob import glob
from dotenv import load_dotenv
from reservoir_utils import ReservoirDataProcessor

# Create instance of reservoir utils class.
reservoir_processor = ReservoirDataProcessor()

# High level directories.
resHome = "/home/nwstg/reservoir"
srvHome = "/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"

# Load environment variables from .env file.
load_dotenv(os.path.join(resHome, '.env'))

# Database credentials.
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')

# Connect to the database.
conn = psycopg2.connect(
   database=db_name, user=db_user, password=db_pass, host=db_host, port=db_port
)

# Create cursor object using the cursor() method.
cursor = conn.cursor()

# Truncate the reservoir table if it exists.
# sql_table_truncate = f"""
# DO $$
# BEGIN
# IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reservoirs_metric') THEN
# TRUNCATE TABLE reservoirs_metric;
# END IF;
# END $$;
# """
# cursor.execute(sql_table_truncate)
# conn.commit()

# Drop the reservoir table is it exists.
sql_table_drop = """DROP TABLE IF EXISTS reservoirs_metric;"""
cursor.execute(sql_table_drop)
conn.commit()

# Create the reservoir table if it does not exist.
sql_table_create = """CREATE TABLE IF NOT EXISTS reservoirs_metric
(reservoir_id text not null, time timestamptz not null, water_level integer null,
battery_voltage real null, data_type char(1) null, unique (reservoir_id, time));"""
cursor.execute(sql_table_create)
conn.commit()

# Create unique index on reservoir table.
sql_index_create = """CREATE UNIQUE INDEX idx_reservoirid_time
ON reservoirs_metric(reservoir_id, time);"""
cursor.execute(sql_index_create)
conn.commit()

# Convert the reservoir table into hypertable.
sql_hypertable_create = """SELECT create_hypertable('reservoirs_metric',
'time', if_not_exists => TRUE);"""
cursor.execute(sql_hypertable_create)
conn.commit()

# Pre-processed csv files.
csv_files = glob(os.path.join(srvHome, 'tsdb', '*-tsdb.csv'))

# Loop through, postprocess, and copy csv contents to reservoir table.
for csv_file in csv_files:

    print('LOG: Updating tsdb with ' + csv_file)

    # Timescale DB insert.
    try:

        # Read the csv into a dataframe.
        df = pd.read_csv(csv_file)
        # Postprocess timescale dataframe prior to db insertion.
        df = reservoir_processor.postprocess_tsdb_df(df)
        # Output postprocessed dataframe to csv prior to db insertion.
        df.to_csv(csv_file, index=False)
        with open(csv_file, 'r') as f:
            next(f)  # Skip header row.
            # Insert to timescale db.
            cursor.copy_from(f, 'reservoirs_metric', sep=',')
            conn.commit()

    except Exception as e:
        print('ERROR: Issue updating tsdb with ' + csv_file)
        print(e)
        continue

# Close connections.
cursor.close()
conn.close()
