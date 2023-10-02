import os
import datetime

import pandas as pd

from glob import glob


class ReservoirDataProcessor:

    def preprocess_reservoir_df(self, station_id, csv_file, indir):

        # Read csv containing all historical data into pandas df.
        df = pd.read_csv(csv_file)

        # Associated production, routinely updating, csv file containing the last month+
        # of data for concatentation with the dataframe containing the full historical
        # archive, associated with the provided csv file. This ensures no data is missed
        # as a result of routine updates while this process is running.
        recent_csv_filename = station_id + '.csv'
        recent_csv_file = os.path.join(indir, recent_csv_filename)

        # Check if production csv exists for concatenation.
        if os.path.exists(recent_csv_file):
            # Dataframe containing last month+ of data for concatentation
            # with the full historical archive.
            recent_df = pd.read_csv(recent_csv_file)
            # Ensure date column is consistent with full archive before
            # concatenation and post-processing.
            recent_df['date'] = pd.to_datetime(recent_df['date']).dt.tz_localize(None)
            # Concatenate full archive and production dataframes to ensure no gaps
            # were introduced while this process was running.
            df = pd.concat([df, recent_df])

        return df

    def postprocess_reservoir_df(self, df):

        # Format date column for new dataframe.
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        # Drop duplicate rows.
        df.drop_duplicates(subset=None, keep='first', inplace=True)
        # Set dataframe index to date.
        df.set_index('date', inplace=True)
        # Sort the dataframe by date.
        df.sort_index(inplace=True)

        return df

    def create_reservoir_csvs(self, station_id, df, outdir):

        # Full csv file to contain all historical data.
        full_csv_filename = station_id + '-full.csv'
        full_csv_file = os.path.join(outdir, full_csv_filename)

        # Latest csv file to contain latest data record.
        latest_csv_filename = station_id + '-latest.csv'
        latest_csv_file = os.path.join(outdir, latest_csv_filename)

        # Recent csv file to contain roughly a month and a half of data.
        recent_csv_filename = station_id + '.csv'
        recent_csv_file = os.path.join(outdir, recent_csv_filename)

        # Date logic for building recent data file.
        current_datetime = datetime.datetime.utcnow()
        start_date = current_datetime - datetime.timedelta(days=43)
        start_date_fmt = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_fmt = current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

        try:
            # Output to production csv files.
            df.to_csv(full_csv_file, date_format='%Y-%m-%dT%H:%M:%SZ')
            df.iloc[-1:].to_csv(latest_csv_file, date_format='%Y-%m-%dT%H:%M:%SZ')
            df[start_date_fmt:end_date_fmt].to_csv(recent_csv_file, date_format='%Y-%m-%dT%H:%M:%SZ')
            return "LOG: Data successfully written to csv files."
        except Exception as e:
            return f"ERROR: Problem writing data to csv files: {str(e)}"

    def preprocess_gina_df(self, indir):

        # Latest files used as reference to get month+ file names.
        latest_files = glob(indir + '/*-latest.csv')

        # Files containing recent month+ of data.
        files = [string.replace('-latest', '') for string in latest_files]

        # # Combine all recent month+ files into single dataframe.
        dfs = []
        for file in files:
            filename = os.path.basename(file)
            station_id = filename.replace('.csv', '')
            if station_id != 'EDD09776':
                df = pd.read_csv(file)
                df['pid'] = station_id
                dfs.append(df)

        # Gina dataframe concatenation.
        gina_df = pd.concat(dfs, ignore_index=True, sort=True)

        return gina_df

    def create_gina_csv(self, df, outdir):

        # Gina csv output files.
        csv_file = os.path.join(outdir, 'gina.csv')
        tmp_csv_file = os.path.join(outdir, 'gina_tmp.csv')

        # Date logic for building recent data file.
        current_datetime = datetime.datetime.utcnow()
        start_date = current_datetime - datetime.timedelta(days=2)
        start_date_fmt = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_fmt = current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Output the last two days of data to csv file.
        df[start_date_fmt:end_date_fmt].to_csv(tmp_csv_file, date_format='%Y-%m-%dT%H:%M:%SZ')

        # Reorder the dataframe columns.
        column_order = ['date', 'data', 'pid', 'bv', 'txtype']
        df = pd.read_csv(tmp_csv_file)
        df = df[column_order]

        try:
            # Output to production gina csv file.
            df.to_csv(csv_file, index=False)
            return "LOG: Data successfully written to gina csv file."
        except Exception as e:
            return f"ERROR: Problem writing data to gina csv file: {str(e)}"
