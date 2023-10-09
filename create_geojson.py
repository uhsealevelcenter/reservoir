import os

import pandas as pd
import numpy as np

from glob import glob
from sklearn.linear_model import LinearRegression
from geojson import Feature, Point, FeatureCollection

# High level data directory.
data_home = "/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"

# Output geojson file.
geojson_file = os.path.join(data_home, "stations.geojson")

# Read reservoir metadata file created by gen_sb program.
reservoir_metadata_file = os.path.join(data_home, "reservoir_metadata.csv")
reservoir_metadata_df = pd.read_csv(reservoir_metadata_file)

# Hardcode other metadata variables.
reservoir_metadata_df['batt_1w_slope'] = 0
reservoir_metadata_df['level_alert'] = 0
reservoir_metadata_df['batt_alert'] = 0

# Production reservoir (43 day) csv files.
reservoir_csv_files = [sub.replace('-latest', '') for sub in glob(os.path.join(data_home, "*-latest.csv"))]

# Loop through and concatenate all recent data to dataframe.
reservoir_csv_data = []
for reservoir_csv_file in reservoir_csv_files:
    if os.path.exists(reservoir_csv_file):
        reservoir_csv_filename = os.path.basename(reservoir_csv_file)
        station_id = reservoir_csv_filename.split('.csv')[0]
        reservoir_csv_df = pd.read_csv(reservoir_csv_file)
        reservoir_csv_df["pid"] = station_id 
        reservoir_csv_data.append(reservoir_csv_df)
reservoir_df = pd.concat(reservoir_csv_data)
reservoir_df.set_index(pd.DatetimeIndex(reservoir_df['date']), inplace=True)
reservoir_df.drop(['date'], axis=1, inplace=True)

# Unique station ids.
pids = reservoir_metadata_df.addr.unique()

# New dataframe containing last 30 days of data for all reservoir stations.
rr = reservoir_df.last('30D')

# Loop through station id's and process data.
for pid in pids:
    dd = rr.loc[rr['pid'] == pid]
    dd = dd.sort_values(by='date',ascending=True)
    dd = dd[~dd.index.duplicated(keep='first')]
    if not dd.empty:
        # Level Alerts
        ee = dd.last('2D')
        nalert = len(ee[(ee['pid']==pid) & (ee['txtype']==6)])
        level_alert = 0
        if nalert > 2:
            level_alert = 1
        # Battery Alrts
        batt_alert = 0
        ee = dd.last('21D')
        ee = ee['bv'].resample('D').mean()
        ee = ee.interpolate(method='linear')
        xx = ee.index.values
        xx = [x.astype('datetime64[s]').astype('int') for x in xx]
        xx = np.array(xx).reshape(-1,1)
        yy = np.array(ee.to_list()).reshape(-1,1)

        linear_regressor = LinearRegression()  # create object for the class
        linear_regressor.fit(xx, yy)  # perform linear regression
        slope = linear_regressor.coef_[0][0]
        Y_pred = linear_regressor.predict(xx)  # make predictions

        if slope < 0:
            batt_alert = 1
            print("BATT ALERT 1")
            print(slope)
        ee = dd.last('1D')
        nalert = len(ee[(ee['pid']==pid) & (ee['bv']<11.5)])
        if nalert > 1:
            batt_alert = 2
            print("BATT ALERT 2")

        nalert = len(ee[ee['bv']<11.5]) / len(ee)
        if nalert > 0.5:
            print(nalert)
            batt_alert = 3
            print ("BATT ALERT 3")

        reservoir_metadata_df.loc[reservoir_metadata_df['addr']==pid,'batt_1w_slope']=slope
        reservoir_metadata_df.loc[reservoir_metadata_df['addr']==pid,'level_alert']=level_alert
        reservoir_metadata_df.loc[reservoir_metadata_df['addr']==pid,'batt_alert']=batt_alert

# Create station geojson file.
features = []
for index, row in reservoir_metadata_df.iterrows():
     # access data using column names
     features.append(Feature(geometry=Point((float(row['lon']),float(row['lat']))),
                             id=str(row['addr']),
                             properties={"name":row['location'],
                                         "dlnrid": str(row['dlnrid']),
                                         "sensor_type": str(row['sensor_type']),
                                         "level_alert_on":row['alert_on'],
                                         "level_alert_off":row['alert_off'],
                                         "batt_alert_on":11.5,
                                         "batt_alert_off":11.7,
                                         "batt_1w_slope":row['batt_1w_slope'],
                                         "level_alert":row['level_alert'],
                                         "batt_alert":row['batt_alert'],
                                        }
                             ))
zz = FeatureCollection(features)
print (zz)
f = open(geojson_file, "w")
f.write(str(zz))
f.close()

# =============================================================================
# X = data.iloc[:, 0].values.reshape(-1, 1)  # values converts it into a numpy array
# Y = data.iloc[:, 1].values.reshape(-1, 1)  # -1 means that calculate the dimension of rows, but have 1 column
# linear_regressor = LinearRegression()  # create object for the class
# linear_regressor.fit(X, Y)  # perform linear regression
# Y_pred = linear_regressor.predict(X)  # make predictions
#
# =============================================================================
