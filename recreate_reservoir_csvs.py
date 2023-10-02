import os
import csv
import datetime
import optparse

import pandas as pd
import gts.gts as gts
import pseudobinary.pseudobinary as pb

from glob import glob

from reservoir_utils import ReservoirDataProcessor

desc = ("Post-process full historical record of reservoir data for the "
        "provided station id and output to production csv files. If no "
        "station id is provided, all stations will be processed.")
usage = "usage: %prog [options] --station_id=STATION_ID"

parser = optparse.OptionParser(description=desc, usage=usage)

# Arguments definition.
parser.add_option('--station_id',
                  dest='station_id',
                  help='station_id',
                  type='string')

(opts, args) = parser.parse_args()

# Station id argument.
station_id = opts.station_id

# Create instance of reservoir utils class.
reservoir_processor = ReservoirDataProcessor()

# High level directories.
resHome = "/home/nwstg/reservoir"
srvHome = "/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"
tmpHome = os.path.join(srvHome, "temp")

# Ensure clean temp directory.
temp_files = glob(tmpHome + '/*.csv')
for temp_file in temp_files:
    os.remove(temp_file)

# Archive of raw data files to post-process.
chunks = glob(resHome + '/../archive_dams/*/???????????????')

# Data validity criteria.
validlen = [61, 64, 129, 201]

# Loop through archive of raw data files to post-process.
for idx, chunkname in enumerate(chunks):

    print('LOG: Processing ' + chunkname)

    # Open and read raw binary input.
    with open(chunkname, 'rb') as f:
        chunk = f.read()
        jd = str(chunkname).split('/')[-1][0:5]
        chunkyear = '20' + jd[-2:]

    # Decode GTS data.
    msg = gts.gts(chunk)

    try:
        # Decode start time and pseudobinary data.
        starttime = (datetime.datetime(int(chunkyear), 1, 1) + datetime.timedelta(days=int(msg.jd)-1, hours=int(msg.msgtime[0:2]), minutes=int(msg.msgtime[2:4])))
        dd = pb.pseudobinary(str(msg.msgbody, 'utf-8'))
    except Exception as e:
        print('ERROR: Issue processing ' + chunkname)
        print(e)
        continue

    # Only process the provided station.
    if (msg.pid == station_id) or (station_id is None):

        # Temporary csv file for output.
        tmp_csv_filename = msg.pid + '-full.csv'
        tmp_csv_file = os.path.join(tmpHome, tmp_csv_filename)

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

            # Dictionary containing data packet of interest.
            data_dict = {'date': times, 'data': dd.data, 'bv': dd.batt, 'txtype': dd.group_id}

            # Dictionary keys for csv generation.
            fieldnames = data_dict.keys()

            # Check if the output csv file already exists for header insertion.
            file_exists = False
            try:
                with open(tmp_csv_file, 'r') as csvfile:
                    file_exists = True
            except FileNotFoundError:
                pass

            # Append data to temporary csv file.
            with open(tmp_csv_file, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # If the file doesn't exist, write the header.
                if not file_exists:
                    writer.writeheader()
                # Determine the number of rows based on the lists in the dictionary.
                num_rows = max(len(val) if isinstance(val, list) else 1 for val in data_dict.values())
                # Write the data.
                for i in range(num_rows):
                    row_data = {}
                    for key, value in data_dict.items():
                        if isinstance(value, list):
                            row_data[key] = value[i] if i < len(value) else ''
                        else:
                            row_data[key] = value
                    writer.writerow(row_data)
            # Close the csv file.
            csvfile.close()

# Temporary files created above containing all historical data to post-process.
tmp_csv_files = glob(tmpHome + '/*-full.csv')

# Loop through temporary csv files to post-process.
for tmp_csv_file in tmp_csv_files:

    # Station id associated with csv file.
    station_id = os.path.basename(tmp_csv_file).replace('-full.csv', '')

    try:
        # Perform dataframe pre and post processing before csv creation.
        df = reservoir_processor.preprocess_reservoir_df(station_id, tmp_csv_file, srvHome)
        df = reservoir_processor.postprocess_reservoir_df(df)
    except Exception as e:
        raise Exception(f"ERROR: {str(e)}")

    # Create production csv files.
    reservoir_processor.create_reservoir_csvs(station_id, df, srvHome)
