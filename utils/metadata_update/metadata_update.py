import pandas as pd
import sqlalchemy as sa
from shapely import wkb
import geopandas as gpd
from dotenv import load_dotenv
import os
import warnings


# Parse lat/lon from Excel
def pos2dd(input):
    hh = input.split("o")[0]
    hemi = hh.split(" ")[0]
    hh = float(hh.split(" ")[1])
    mm = input.split("o")[1].split("'")

    ss = float(mm[1].split('"')[0])
    mm = float(mm[0])

    dd = hh + (mm / 60) + (ss / 3600)

    if hemi == "S" or hemi == "W":
        dd = dd * -1

    return dd


# Read Excel and return metadata dataframe.
def read_dam_excel(xls_path):
    # Read dams excel file.
    stns = pd.read_excel(xls_path)

    # # Initialize empty dataframe.
    reservoir_metadata_df = pd.DataFrame(
        columns=[
            "station_id",
            "dlnrid",
            "name",
            "lat",
            "lon",
            "level_alert_on",
            "level_alert_off",
            "sensor_type",
        ]
    )

    # Loop through unique stations and append to dataframe.
    for stn in stns.ADDRESS:
        if isinstance(stn, str):
            foo = stns.loc[stns["ADDRESS"] == stn].to_dict("records")
            if str(foo[0]["DLNR #"]) != "nan" and str(foo[0]["Status"]) != "removed":
                # create clean df here
                tempdf = pd.DataFrame(
                    {
                        "station_id": [foo[0]["ADDRESS"]],
                        "dlnrid": [str(foo[0]["DLNR #"])],
                        "name": [str(foo[0]["LOCATION"])],
                        "lat": [pos2dd(foo[0]["LAT"])],
                        "lon": [pos2dd(foo[0]["LONG"])],
                        "level_alert_on": [foo[0]["5 MIN ON"]],
                        "level_alert_off": [foo[0]["5 MIN OFF"]],
                        "sensor_type": [foo[0]["Sensor type"]],
                    }
                )
                tempdf["sensor_type"] = tempdf["sensor_type"].fillna("None")
                reservoir_metadata_df = reservoir_metadata_df.append(tempdf)

    reservoir_metadata_df = reservoir_metadata_df.reset_index(drop=True)

    return reservoir_metadata_df


# Get current metadata from wyrtki database.
def get_db_metadata(db_url):
    engine = sa.create_engine(db_url)

    conn = engine.connect()
    query = """
        SELECT station_id, dlnrid, name, level_alert_on, level_alert_off, batt_alert_on,
        batt_alert_off, sensor_type, geom as geometry
        FROM public.reservoir_metadata
    """
    data = pd.DataFrame(conn.execute(sa.text(query)))
    conn.close()

    # Convert geometry from binary (wkb) to text (wkt) to latitude/longitude
    # I think there are more sophisticated ways to deal with PostGIS in SQLAlchemy/GeoAlchemy2 but this works...
    data.geometry = data.geometry.apply(wkb.loads)
    data = gpd.GeoDataFrame(data, geometry="geometry", crs="epsg:4326")
    data.loc[:, "lat"] = data.geometry.y
    data.loc[:, "lon"] = data.geometry.x

    return data


# Compare spreadsheet to database and return lists of new stations to insert and station values to update.
# New stations to insert will be returned as a list with a dict of all fields for each station.
# Value updates will be returned in a list of dicts like this:
# {station_id: station1, update_field1: new_value1, update_field2: new_value2}
def find_changed_values(xls_path, db_url):
    db_data = get_db_metadata(db_url)
    xls_data = read_dam_excel(xls_path)

    # Round latitude/longitude to avoid slight mismatches
    db_data[["lat", "lon"]] = db_data[["lat", "lon"]].round(4)
    xls_data[["lat", "lon"]] = xls_data[["lat", "lon"]].round(4)

    xls_col = [
        col for col in xls_data
    ]  # Exclude columns that are not in spreadsheet (batt_alerts, geometry)
    merged_df = db_data[xls_col].merge(xls_data, indicator=True, how="outer")
    updated_rows = merged_df.loc[
        merged_df._merge == "right_only"
    ]  # Find different rows in right df (xls_data)
    updated_rows = updated_rows[
        [col for col in updated_rows if col != "_merge"]
    ]  # Get rid of merge indicator

    # Create list of dicts for value updates/new stations
    updated_values = []
    new_stations = []

    for row in updated_rows.iterrows():
        station_id = row[1].station_id

        # New station to be inserted (station_id is not currently in database)
        if station_id not in db_data.station_id.values:
            new_record = row[1].to_dict()
            # Add default battery alerts since these are not in spreadsheet
            new_record.update({"batt_alert_on": 11.5, "batt_alert_off": 11.7})
            # Could create geometry (point from lat, lon) here...
            new_stations.append(new_record)

        # Update of a station that already exists in the db
        else:
            current_row = db_data.loc[db_data.station_id == station_id, xls_col]
            update_dict = {"station_id": station_id}
            for col in xls_col:
                if current_row[col].iloc[0] != row[1][col]:
                    update_dict.update({col: row[1][col]})
            updated_values.append(update_dict)

    return updated_values, new_stations


#### Use SQLAlchemy/whatever to make changes... ####


if __name__ == "__main__":
    load_dotenv(override=True)

    # Kyrstin local configuration
    db_local = os.getenv("DB_URL_DEV")
    xls_local = os.getenv("XLS_LOCAL")

    # Wyrtki configuration
    db_srv = os.getenv("DB_URL")
    xls_srv = os.getenv("XLS_SRV")

    # This suppresses the annoying FutureWarning from pandas about append method deprecation (used in pos2dd)
    warnings.simplefilter(action="ignore", category=FutureWarning)

    updates, inserts = find_changed_values(db_url=db_local, xls_path=xls_local)
