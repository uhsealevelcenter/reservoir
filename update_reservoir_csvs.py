import os
import shutil
import datetime
import psycopg2

import pandas as pd
import gts.gts as gts
import pseudobinary.pseudobinary as pb

from glob import glob

from reservoir_utils import ReservoirDataProcessor

# Create instance of reservoir utils class.
reservoir_processor = ReservoirDataProcessor()

# High level directories.
resHome = "/home/nwstg/reservoir"
srvHome = "/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"

# Csv file containing data routinely inserted to timescale db.
tsdb_csv = os.path.join(resHome, 'tsdb_insert.csv')

# Database credentials.
db_name = 'uhslc'
db_user = 'postgres'
db_pass = 'password'
db_host = 'wyrtki'  # Same as putting wyrtki.soest.hawaii.edu or 127.0.0.1 here
db_port = '5432'

# Connect to the database.
conn = psycopg2.connect(
   database=db_name, user=db_user, password=db_pass, host=db_host, port=db_port
)

# Raw data files to post-process.
chunks = glob(resHome + '/../dams/???????????????')

# Data validity criteria.
validlen = [61, 64, 129, 201]

# Loop through raw data files to post-process.
for idx, chunkname in enumerate(chunks):

    print('LOG: Processing ' + chunkname)

    # Open and read raw binary input.
    with open(chunkname, 'rb') as f:
        chunk = f.read()
        jd = str(chunkname).split('/')[-1][0:5]

        # Archive raw data.
        try:
            path = resHome + '/../archive_dams/' + jd
            os.makedirs(path, exist_ok=True)
            shutil.move(chunkname, path)
        except Exception as e:
            print('ERROR: Issue archiving ' + chunkname)
            print(e)
            pass

    # Decode GTS data.
    msg = gts.gts(chunk)

    try:
        # Decode start time and pseudobinary data.
        starttime = (datetime.datetime(datetime.datetime.utcnow().year, 1, 1) + datetime.timedelta(days=int(msg.jd)-1, hours=int(msg.msgtime[0:2]), minutes=int(msg.msgtime[2:4])))
        dd = pb.pseudobinary(str(msg.msgbody, 'utf-8'))
    except Exception as e:
        print('ERROR: Issue decoding ' + chunkname)
        print(e)
        continue

    # Data validity checks.
    chunklen = (len(chunk))
    numpts = len(dd.data)
    if numpts > 0 and chunklen in validlen:

        # This is the one station with 2 sensors, but we dont care about the 2nd one.
        if msg.pid == 'EDD02A2A' and numpts == 48:
            numpts = 24
            dd.data = dd.data[0:24]
        if msg.pid == 'EDD02A2A' and numpts == 2:
            numpts = 1
            dd.data = dd.data[0:1]

        # Step through data times.
        st = starttime
        step = datetime.timedelta(minutes=-5)
        times = []
        count = 0
        while numpts > count:
            times.append(st)
            st += step
            count += 1

        # Timescale DB insert.
        try:

            # Timezone aware timestamps for insert to timescale db.
            timestamptzs = [timestamp.replace(tzinfo=datetime.timezone.utc) for timestamp in times]
            # Construct dataframe for insert to timescale db.
            tsdb_dict = {'reservoir_id': msg.pid, 'time': timestamptzs, 'water_level': dd.data,
                         'bv': dd.batt, 'data_type': dd.group_id}
            tsdb_df = pd.DataFrame(tsdb_dict)
            # Postprocess timescale dataframe prior to db insertion.
            tsdb_df = reservoir_processor.postprocess_tsdb_df(tsdb_df)
            # Output timescale dataframe to csv for database insert.
            tsdb_df.to_csv(tsdb_csv, index=False, header=False)
            # Insert latest reservoir data into timescale db.
            reservoir_processor.insert_reservoir_csv_to_timescale(conn, 'reservoirs_metric', tsdb_csv)

        except Exception as e:
            print('ERROR: Issue updating tsdb with data from ' + chunkname)
            print(e)
            pass

        # Production csv file creation.
        try:

            # Dictionary containing data packet of interest.
            data_dict = {'date': times, 'data': dd.data, 'bv': dd.batt, 'txtype': dd.group_id}

            # Dataframe of above dict containing latest data.
            new_data_df = pd.DataFrame(data_dict)

            # Format the date column for the dataframe.
            new_data_df['date'] = pd.to_datetime(new_data_df['date']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Full historical csv file containing all historical data.
            full_csv_filename = msg.pid + '-full.csv'
            full_csv_file = os.path.join(srvHome, full_csv_filename)

            # Check if the full historical csv file exists.
            file_exists = False
            try:
                with open(full_csv_file, 'r') as csvfile:
                    file_exists = True
            except FileNotFoundError:
                pass

            # If the full historical csv file doesn't exist, create a new dataframe with
            # the latest data, otherwise append the latest data to the full dataframe.
            if not file_exists:
                df = new_data_df
            else:
                full_df = pd.read_csv(full_csv_file)
                df = pd.concat([full_df, new_data_df])

            # Perform dataframe post processing before production csv file creation.
            df = reservoir_processor.postprocess_reservoir_df(df)

        except Exception as e:
            print('ERROR: Issue updating production csvs with data from ' + chunkname)
            print(e)
            continue

        # Create production csv files.
        reservoir_processor.create_reservoir_csvs(msg.pid, df, srvHome)

try:
    # Perform dataframe pre and post processing before gina csv file creation.
    df = reservoir_processor.preprocess_gina_df(srvHome)
    df = reservoir_processor.postprocess_reservoir_df(df)
    # Create final gina csv file.
    reservoir_processor.create_gina_csv(df, srvHome)
except Exception as e:
    print('ERROR: Issue updating production gina csv file.')
    print(e)
    pass

# Close the database connection.
conn.close()
