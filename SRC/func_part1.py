import json
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from descartes import PolygonPatch
from pymongo import MongoClient
from shapely.geometry import Point


# Function to open a json file
def read_json (path):
    with open(path, 'r') as file:
        docjson=file.read()
    return json.loads(docjson)


# Function to get location data from a json file
def getDataFromJson (row): #row = res_json[0]
    return {
        "Code": row["code"],
        "Latitude": float(row["lat"]),
        "Longitude": float(row["lon"]),
        "Country": row["country"]
    }


# Function to convert a json file into a dataframe
def fromJsonToDF (path):
    res_json = read_json(path)
    data = list(map(getDataFromJson, res_json))
    return pd.DataFrame(data)


# Function to convert a CSV into a DF
def fromCSVToDF (path):
    csv = pd.read_csv(path)
    csv = csv.dropna(axis = 0)
    csv = csv[["Country", "Latitude", "Longitude"]]
    return csv.rename(columns = {"Country": "Code"})


# Function to connect to Mongo dataset
def getDataFromMongoDB (dbName, collName):
    mongodbURL = f"mongodb://localhost/{dbName}"
    client = MongoClient(mongodbURL)
    db = client.get_database() # Gets all the databases from the client
    cursor = eval(f"db.{collName}") # Selecting the companies database
    return cursor


# Function to get a DF from MongoDB
def getDFfromMongoDB (dbName, collName, myquery, fields):
    cursor = getDataFromMongoDB (dbName, collName)
    lista = list(cursor.find(myquery, fields))
    return pd.DataFrame(lista)


# Function to separate into columns
def separateColumns(row):
    office = row["offices"]
    if office:
        return {
            "Country": office[0]["country_code"],
            "Latitude": office[0]["latitude"],
            "Longitude": office[0]["longitude"]
        }


#Function to clean a DF coming from MongoDB
def cleanDFMongo (df):
    df = df.apply(separateColumns, axis=1, result_type="expand")
    #Clean DF
    df = df.dropna(axis = 0)
    df = df.reset_index(drop = True)
    df = df.rename(columns = {"Country": "Code"})
    return df


# Function to find the elements of a dataframe within a location
def findingLocation (df, latmin, latmax, longmin, longmax):
    lista=[]
    for i in df.index:
        if (df["Latitude"][i] >= latmin and df["Latitude"][i] <= latmax
           and df["Longitude"][i] >= longmin and df["Longitude"][i] <=longmax):
            lista.append({"Code": df["Code"][i],
                          "Latitude": df["Latitude"][i],
                          "Longitude": df["Longitude"][i]
                             })
    return pd.DataFrame(lista)


# Function to do a Bubble plot
def bubbleplot(df, names, colors, markerSize):
    fig = go.Figure()

    for i in range(len(df)):
        df_sub = df[i]
        fig.add_trace(go.Scattergeo(
            locationmode = "ISO-3",
            lat = df_sub['Latitude'],
            lon = df_sub['Longitude'],
            text = df_sub['Code'],
            marker = dict(
                size = markerSize[i],
                color = colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode = 'area'),
            name = names[i]))
        
    fig.update_layout(
        title_text = "Airports, Starbucks and <br>old companies in Europe",
        showlegend = True,
        geo = dict(
            scope = 'europe',
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    
    fig.show()


# Function to create a circle, given a center (x,y) and a radius (r)
# For a higher resolution when plotting, we convert the units from degrees to km
def CreateCircle (row, r):
    x = row["Longitude"]*111 # 1 degree = 111 km
    y = row["Latitude"]*111 
    R = r
    return Point(x, y).buffer(R) # buffer indicates that it is a circle-shaped polygon


# Function to add the Circle (polygon) to the DF
def addAreaToDF (df, r):
    pointSeries = df.apply(lambda x: CreateCircle(x,r), axis = 1)
    pointdf = pd.DataFrame(columns = {"Area"}, data = pointSeries)
    return pd.concat([df, pointdf], axis = 1)


# Function to plot and calculate the allowed area to locate the company
def areaPlot(df, colors, names):
    areatot = 0

    fig,ax = plt.subplots(figsize= (8,8))

    for i in df[0].index:
        aer = PolygonPatch(df[0]["Area"][i], facecolor='w', edgecolor = colors[0]) # Plot area df[0]
        ax.add_patch(aer)

        for j in df[1].index:
            star = PolygonPatch(df[1]["Area"][j], facecolor='w', edgecolor = colors[1]) # Plot area df[1]
            ax.add_patch(star)
            
            # Intersection between df[0] and df[1]
            inter = df[0]["Area"][i].intersection(df[1]["Area"][j])

            for k in df[2].index:  
                old = PolygonPatch(df[2]["Area"][k], facecolor='w', edgecolor = colors[2]) # Plot area df[2]
                ax.add_patch(old)
                
                # Difference between Intersection and df[3]
                dif = inter.difference(df[2]["Area"][k])
                inter = dif

                if dif:
                    patch = PolygonPatch(dif, facecolor='#f8f65f', edgecolor='#f8f65f')
                    ax.add_patch(patch)
            areatot += dif.area

    plt.xlim(-430,-380)
    plt.ylim(4470,4510)
    plt.xlabel("Longitude (km)", fontsize=12)
    plt.ylabel("Latitude (km)", fontsize=12)
    plt.title("Optimum areas", fontsize=18)
    ax.legend(names)
    return areatot