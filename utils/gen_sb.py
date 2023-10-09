import os

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


# High level data directory.
data_dir = "/srv/htdocs/uhslc.soest.hawaii.edu/reservoir"

# Reservoir metadata file and html file for selectbox.
reservoir_metadata_file = os.path.join(data_dir, "reservoir_metadata.csv")
sb_html_file = os.path.join(data_dir, "selectbox.html")

# Data for selectbox.html.
sb = """<script type="text/javascript">
  $('select').select2();
</script>

<form action="">
  <div style=""><font size="+1">Station:</font></div>
  <div style=""><select name="stn" class="select2">
"""

# Read dams excel file.
stns = pd.read_excel('/home/ilikai10/slctech/DAM/DAM allocations master.xlsx')

# Initialize empty dataframe.
reservoir_metadata_df = pd.DataFrame(columns=['addr','dlnrid','location','lat','lon','alert_on','alert_off', 'sensor_type'])

# Loop through unique stations and append to dataframe.
for stn in stns.ADDRESS:
    if isinstance(stn,str):
        foo = stns.loc[stns['ADDRESS'] == stn].to_dict('r')
        if str(foo[0]['DLNR #']) != 'nan' and str(foo[0]['Status']) != 'removed':
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
                                  "alert_off":[foo[0]['5 MIN OFF']],
                                  "sensor_type":[foo[0]['Sensor type']]
                                  })
            tempdf['sensor_type'] = tempdf['sensor_type'].fillna('None')
            reservoir_metadata_df = reservoir_metadata_df.append(tempdf)
            
reservoir_metadata_df = reservoir_metadata_df.reset_index()

# Data for selectbox.html.
sb += """  </select></div>
</form>
"""

# Create selectbox.html.
f = open(sb_html_file, "w")
f.write(sb)
f.close()

# Create metadata csv file.
reservoir_metadata_df.to_csv(reservoir_metadata_file, index=False, header=True, float_format='%.4f')
