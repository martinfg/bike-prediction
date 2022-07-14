# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: nextbike-prediction
#     language: python
#     name: nextbike-prediction
# ---

# %% [markdown]
# # Exploration of Data of Nextbike-API

# %% [markdown]
# ### Observations / Assumptions
#
# - we can only see bikes which are free or reserved (booked) right now, we can't see bikes which are currently rented
# - available bikes includes the number of bikes which are reserved (booked)
# - the number of available bikes is 1349, this is the number we must get after preprocessing
# - we assume that there are two different kind of places:
#     - bike stations (spot=True and bike=False) where multiple bikes are assigned to one location
#     - individual bikes (spot=False and bike=True) where each bike has an own location
# - booked_bikes seems to mean the bikes that have been reserved in advance. So bikes_available_to_rent = bikes - booked_bikes
# - UIDs of bike stations seem to be in a different range than UIDs of bikes
#     
# ### Open questions
#
# - What is the mapping of the bike types? 71, 150, 183, 196? Maybe one of them code for e-bikes?? Is this relevant for our prediction?
# - At a station where there are multiple bikes and some of them are reserved (booked), can we find out which of them is reserved and which is free?
# - What are the different place types?
#
# ### Preprocessing
#
# - Keep all information from place-, city- and bike-list-section per bike
# - Maybe use [JQ](https://stedolan.github.io/jq/manual/) to filter the data and build a JSON that can be easily read by pandas 
# - Parse name of place correctly (e.g. Straße)
# - Filter out the reserved bikes?

# %%
from IPython.display import display, HTML
display(HTML("<style>.container { width:95% !important; }</style>"))

# %%
# #%matplotlib notebook

# %%
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt 
import json
import plotly.graph_objects as go

# %%
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# %% [markdown]
# ### Load sample data from API call

# %%
file_path = '../sample_data/bikes.json'

# %%
with open(file_path, 'r') as f:
    data = json.load(f)

# %%
data_leipzig = data['countries'][0]['cities'][0]

# %%
data_leipzig

# %%
places = data_leipzig['places']
print(len(places))

# %% [markdown]
# It makes sense that we get less places than available bikes since there are places without any bikes assigned and places with multiple bikes.

# %%
bike_stations = [p for p in places if p['spot'] == True and p['bike'] == False]
len(bike_stations)

# %% [markdown]
# There were 71 stations during this API call, let's see if that number changes when we take an API call with another timestamp.

# %%
free_bikes = [p for p in places if p['spot'] == False and p['bike'] == True]
len(free_bikes)

# %%
places_with_booked_bikes = [p for p in places if p['bikes_available_to_rent'] < p['bikes']]
places_with_booked_bikes

# %%
assert len(bike_stations) + len(free_bikes) == len(places), "the number of bike stations and free bikes should add up to the number of all places"
assert len(free_bikes) == len([b for b in free_bikes if b['bike'] == 1]), "following our assumption, there should be no individual bike with a bike count different from 1"

amount_bikes = 0

for p in places:
    amount_bikes += len(p['bike_list'])
    
assert data_leipzig['available_bikes'] == amount_bikes, "following our assumption, the number of available bikes should be equal to the number of bikes appearing in the bike_lists"

amount_booked_bikes = 0

for p in places_with_booked_bikes:
    amount_booked_bikes += p['bikes'] - p['bikes_available_to_rent']
    
assert data_leipzig['booked_bikes'] == amount_booked_bikes, "following our assumption, the number of booked bikes should be equal to the number of total bikes minus the number of bikes available to rent"

# %%
bike_stations

# %% [markdown]
# ### Get Location of bikes
#
# - Extract geo locations from the lists we built out of the JSON file and put them in a dictionary.

# %%
free_bike_locations = {}
station_bike_locations = {}

for p in free_bikes:
    for bike in p['bike_list']:
        free_bike_locations.update({bike['number']: {'lat': p['lat'], 'lng': p['lng']}})
        
for p in bike_stations:
    for bike in p['bike_list']:
        station_bike_locations.update({bike['number']: {'lat': p['lat'], 'lng': p['lng']}})

# %%
stations = {}
for p in bike_stations:
    stations.update({p['number']: {'name': p['name'], 'lat': p['lat'], 'lng': p['lng'], 'bikes': p['bikes'], 'bikes_available_to_rent': p['bikes_available_to_rent']}})

# %%
free_bike_locations_df = pd.DataFrame.from_dict(free_bike_locations, orient='index')
station_bike_locations_df = pd.DataFrame.from_dict(station_bike_locations, orient='index')
stations_df = pd.DataFrame.from_dict(stations, orient='index')

# %%
free_bike_locations_df.head()

# %%
len(free_bike_locations)

# %%
station_bike_locations_df.head()

# %%
len(station_bike_locations_df)

# %%
stations_df.head()

# %%
len(stations_df)

# %% [markdown]
# - It would be nice to have an additional attribute from type list which contains all related bike numbers.
# - Also it would be great to parse the strings correctly so that we can see the "Umlaute".

# %% [markdown]
# ## Plot bikes on map

# %%
mapbox_access_token = "pk.eyJ1IjoiYW5kcmVhc2tpeiIsImEiOiJjbDR1MXBseW4wdnl3M2NudTV2djhmOGRkIn0.ziKnGcQULxdwxhkAjiJBHg"

fig = go.Figure()

# add station markers to map
for index, row in stations_df.iterrows():
    fig.add_trace(go.Scattermapbox(
        lat=[row['lat']],
        lon=[row['lng']],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='#1e3799'            
        ),
        text="Station " + str(index),
        name=row['name']
        ))

# add free bike markers to map (only head because it starts lagging otherwise)
for index, row in free_bike_locations_df.head(100).iterrows():
    fig.add_trace(go.Scattermapbox(
        lat=[row['lat']],
        lon=[row['lng']],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='#e84118'            
        ),
        text="Bike " + str(index),
        ))
    
fig.update_layout(
    mapbox_style="satellite",
    height=800,
    width=1200,
    margin=go.layout.Margin(
        l=0, # left margin
        r=0, # right margin
        b=0, # bottom margin
        t=0, # top margin
    ),
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=51.34083402293,
            lon=12.375113185144219
        ),
        pitch=0,
        zoom=10
    )
)

fig.update_layout(showlegend=False)

fig.show()

# %%
locations = [{'id': b['uid'],'latitude': b['lat'], 'longitude': b['lng'] } for b in bikes]

# %%
locations_df = pd.DataFrame(locations)

# %%
locations_df.head(5)

# %% [markdown]
# ### Debug locations

# %%
northest_bike_loc = [northest_bike['latitude'], northest_bike['longitude']]
northest_bike_loc

# %%
northest_bike

# %%
northest_bike = min(locations, key=lambda x: x['longitude'])

# %% [markdown]
# #### What's beneath here is trash

# %%
# possible reading with pandas
bike_df = pd.json_normalize(data=data['countries'], record_path=['cities', 'places', 'bike_list'],
                               meta=['lat', 'lng',
                                    'show_bike_types', 'show_bike_type_groups',
                                    'show_free_racks', 'booked_bikes', 'set_point_bikes', 'available_bikes',
                                    ])

# meta information i dropped: pricing, faq_url, name, language, cities, 'store_uri_android', 'store_uri_ios', website, policy, 'system_operator_address', 'country', 'country_name', 'terms', 'policy', 'name', 'hotline'
# domain, language, email, zoom, currency, country_calling_code, no_registration, 'capped_available_bikes'
bike_df.head(3)
