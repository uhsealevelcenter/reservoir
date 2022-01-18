#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 19:41:49 2020

@author: dyoung
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from geojson import Feature, Point, FeatureCollection

cleanstn= pd.read_pickle('dam_meta.pkl')
reservoirs = pd.read_pickle('reservoir.pkl')
reservoirs = reservoirs.set_index(pd.DatetimeIndex(reservoirs['date']))
# this is kind of dumb...
reservoirs = reservoirs.drop(['date'], axis=1)

pids=cleanstn.addr.unique()

cleanstn['batt_1w_slope'] = 0
cleanstn['level_alert'] = 0
cleanstn['batt_alert'] = 0

rr = reservoirs.last('30D')
for pid in pids:
    dd = rr.loc[rr['pid'] == pid]
    #calculate stuff here
    dd = dd.sort_values(by='date',ascending=True)
    dd = dd[~dd.index.duplicated(keep='first')]
    #dd.drop_duplicates(inplace=True)
    #print(pid)

    if not dd.empty:
        # Level Alerts
        ee = dd.last('2D')
        nalert = len(ee[(ee['pid']==pid) & (ee['txtype']==6)])
        level_alert = 0
        if nalert > 2:
            level_alert = 1
            #print("level alert")

        # Battery Alrts
        batt_alert = 0
        ee = dd.last('21D')
        ee = ee['bv'].resample('D').mean()
        ee = ee.interpolate(method='linear')
        #ee = ee.fillna(method='ffill')
        xx = ee.index.values
        xx = [x.astype('datetime64[s]').astype('int') for x in xx]
        xx = np.array(xx).reshape(-1,1)
        yy = np.array(ee.to_list()).reshape(-1,1)

        linear_regressor = LinearRegression()  # create object for the class
        linear_regressor.fit(xx, yy)  # perform linear regression
        slope = linear_regressor.coef_[0][0]
        #print(slope)
        Y_pred = linear_regressor.predict(xx)  # make predictions

        #if slope < -10e-8:
        if slope < 0:
            batt_alert = 1
            print("BATT ALERT 1")
            print(slope)

            
        ee = dd.last('1D')
        nalert = len(ee[(ee['pid']==pid) & (ee['bv']<11.5)])
        if nalert > 1:
            batt_alert = 2
            print("BATT ALERT 2")
        
        #nalert = len(ee[(ee['pid']==pid) & (ee['bv'] < 11.5)]) / len(ee[(ee['pid']==pid) & (ee['bv'])])
        nalert = len(ee[ee['bv']<11.5]) / len(ee)
        #print (len(ee))
        if nalert > 0.5:
            print(nalert)
            batt_alert = 3
            print ("BATT ALERT 3")

        cleanstn.loc[cleanstn['addr']==pid,'batt_1w_slope']=slope
        cleanstn.loc[cleanstn['addr']==pid,'level_alert']=level_alert
        cleanstn.loc[cleanstn['addr']==pid,'batt_alert']=batt_alert
    

features = []
for index, row in cleanstn.iterrows():
     # access data using column names
     features.append(Feature(geometry=Point((float(row['lon']),float(row['lat']))), 
                             id=str(row['addr']), 
                             properties={"name":row['location'], 
                                         "dlnrid": str(row['dlnrid']),
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
f = open("stations.geojson","w")
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

