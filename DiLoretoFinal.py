'''Danielle DiLoreto
CS-299 Final'''

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import mapbox as mb
import csv
from PIL import Image
import statistics as stat

MAPKEY = "pk.eyJ1IjoiZGlsb3JldDBkYW5pIiwiYSI6ImNrOWxrOWNpbjAwcjEzbHB4YXdvbmozMDYifQ.rb6d8wXP7ukeAVZUrdonSw"

def read_data(filename):
    airbb_data = {}
    data = open(filename, 'r', encoding="utf8")
    read1 = pd.read_csv(data)

    city =read1['neighbourhood'].values.tolist()
    id = read1['id'].values.tolist()
    name = read1['name'].values.tolist()
    lat = read1['latitude'].values.tolist()
    long = read1['longitude'].values.tolist()
    room_type = read1['room_type'].values.tolist()
    price = read1['price'].values.tolist()

    # add each list as a key:value pair to the browser_data dict
    airbb_data['city'] = city
    airbb_data['id'] = id
    airbb_data['name'] = name
    airbb_data['latitude'] = lat
    airbb_data['longitude'] = long
    airbb_data['room_type'] = room_type
    airbb_data['price'] = price

    return airbb_data

def UI(data):
    image = Image.open("airbnb.png")
    #add a logo for airbnb
    st.image(image, caption=None, width=None,
                    use_column_width=False, clamp=False, channels='RGB', format='PNG') #https://docs.streamlit.io/api.html#display-media
    st.header("Using Airbnb in Boston")
    # get user input for max price and home type preference
    maxPrice = st.slider('Max Price You Are Willing to Spend',0.0,10000.0,50.0)
    roomType= st.radio(
    'Room Type: ',
    ('Private room', 'Entire home/apt', 'Hotel room', 'Shared room')
    )

    # neighborhood radio buttons
    neighborhood = []
    neighborhoods = data['city']
    for key in neighborhoods:
        if key not in neighborhood:
            neighborhood.append(key)
        else: continue
    st.write("Neighborhood")
    city = st.selectbox("Select a neighborhood: ", neighborhood)


    # loop over each item in each list within the data dict to make a new list of the selected city
    # this checks for data that meets the user input conditions
    mapLocations= []
    thisCityPrices = { 'Private room' : [], 'Entire home/apt' : [], 'Hotel room' : [], 'Shared room' : [] }
    for item in range(len(data['city'])):
        thisCity = data['city'][item]
        thisPrice = data['price'][item]
        thisRoom = data['room_type'][item]
        # get the specific listings that meet user criteria
        if thisCity == city and thisPrice <= maxPrice and roomType in thisRoom:
            thisID = data['id'][item]
            thisLat = data['latitude'][item]
            thisLon = data['longitude'][item]
            mapLocations.append((thisID, thisLat, thisLon))
        # use this to create pricing dict, and get neighborhood average room pricing for each room type
        if thisCity == city:
            thisCityPrices[thisRoom].append(thisPrice)

#calculate the average price per room type in the area that the user selected
    roomTypes = []
    avgPrices = []
    for key in thisCityPrices:
        prices = thisCityPrices[key]
        roomTypes.append(key)
        if prices != []:
           meanPrice = stat.mean(prices)
           avgPrices.append(meanPrice)
        else:
            meanPrice = 0
            avgPrices.append(meanPrice)
     #creating a map
    df = pd.DataFrame(mapLocations, columns=["id", "lat", "lon"])
    if df.empty == True:
        st.write("No matching records")
    else:
        st.title("Airbnb Listings")
        st.dataframe(df)
        #simple map
        #st.map(df)

        view_state = pdk.ViewState(
          latitude=df["lat"].mean(),
          longitude=df["lon"].mean(),
          zoom=13,
          pitch=5)


        layer1 = pdk.Layer('ScatterplotLayer',
                           data=df,
                           get_position='[lon, lat]',
                           get_radius=50,
                           get_color=[100,0,150],
                           pickable=True
                          )

        tool_tip = {"html" : "This Airbnb id is: <br/> <b>{id}</b>" ,
                        "style": { "backgroundColor": "steelblue",
                                   "color": "white"}
                       }

        map = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state,
                mapbox_key=MAPKEY,
                layers=[layer1],
                tooltip= tool_tip
            )
        st.pydeck_chart(map)

    #plot the interactive bar chart

    fig, axes = plt.subplots()
    values = avgPrices
    axes.set_title('Average Price for Each Room Type in ' + city)
    axes.bar(roomTypes,values, color=['magenta', 'red', 'green', 'cyan'])
    axes.set_ylabel("Average Price")
    axes.set_xlabel("Room Type")
    st.pyplot(plt) #https://stackoverflow.com/questions/58237086/how-to-animate-a-line-chart-in-a-streamlit-page




def getLocations(data):
    locations = []
    for item in range(len(data['city'])):
        id = data['id'][item]
        lat = data['latitude'][item]
        long = data['longitude'][item]
        locations.append((id, lat, long))

    return locations

if __name__ == "__main__":

    # get the airbnb listing filename
    filename = 'airbblistings.csv'

    # create a data frame of all of the airbnb data
    data = read_data(filename)

    # get list of airbnb locations
    locations = getLocations(data)

    # create the interactive map and graph for streamlit UI
    UI(data)







