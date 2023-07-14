#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 10:25:22 2020

@author: dyoung
"""

import pandas as pd

def pos2dd(input):
    hh = input.split('o')[0]
    hemi = hh.split(' ')[0]
    hh = float(hh.split(' ')[1])
    mm = input.split('o')[1].split("'")

    ss = float(mm[1].split('"')[0])
    mm = float(mm[0])

    dd = hh + (mm/60) + (ss/3600)
    
    if hemi == 'S' or hemi == 'W':
        dd = dd * -1
    
    return dd


sb = """<script type="text/javascript">
  $('select').select2();
</script>

<form action="">
  <div style=""><font size="+1">Station:</font></div>
  <div style=""><select name="stn" class="select2">
"""

# stns = pd.read_excel('DAM allocations master.xlsx')
stns = pd.read_excel('/home/ilikai10/slctech/DAM/DAM allocations master.xlsx')

cleanstn=pd.DataFrame(columns=['addr','dlnrid','location','lat','lon','alert_on','alert_off'])

for stn in stns.ADDRESS:
    if isinstance(stn,str):
        foo = stns.loc[stns['ADDRESS'] == stn].to_dict('r')
        if str(foo[0]['DLNR #']) != 'nan':
            sb += '      <option value="{}">{} {} {}</option>\n'.format(str(foo[0]['ADDRESS']),
                                                                        str(foo[0]['ADDRESS']),
                                                                        str(foo[0]['DLNR #']),
                                                                        str(foo[0]['LOCATION']))
            # create clean df here
            tempdf = pd.DataFrame({"addr":[foo[0]['ADDRESS']], 
                                  "dlnrid":[str(foo[0]['DLNR #'])], 
                                  "location":[str(foo[0]['LOCATION'])],
                                  "lat":[pos2dd(foo[0]['LAT'])],
                                  "lon":[pos2dd(foo[0]['LONG'])],
                                  "alert_on":[foo[0]['5 MIN ON']],
                                  "alert_off":[foo[0]['5 MIN OFF']]
                                  })
            cleanstn = cleanstn.append(tempdf)
            
cleanstn = cleanstn.reset_index()
            
sb += """  </select></div>
</form>
"""

#print(sb)
f = open("selectbox.html","w")
f.write(sb)
f.close()

cleanstn.to_pickle('dam_meta.pkl')
        



