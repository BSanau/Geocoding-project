import json, requests, os
import matplotlib.pyplot as plt
import pandas as pd
from descartes import PolygonPatch
from dotenv import load_dotenv
from geopandas import GeoDataFrame
from shapely.geometry import Point

#Function to find the {code} near a location {point}
def APIFoursquare (code, point):
    # Getting token from environment
    load_dotenv()
    apiID = os.getenv("CLIENT_ID")
    apiKey = os.getenv("CLIENT_SECRET") 
    #return f"{apiID[0:3]}, {apiKey[0:3]}"
    
    # Connecting to Foursquare API
    url = "https://api.foursquare.com/v2/venues/explore"

    params = {
        "client_id": apiID, 
        "client_secret": apiKey,
        "v": "20180323", #versioning
        "ll": point, #latitude, longitude
        "query": code,
        "limit": 50 #search 50 items    
    }

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)
    return data


# Function to get the Latitude, Longitude and Distance of a result
def GetLocationData (row):
    return {
        "Latitude": row["venue"]["location"]["lat"],
        "Longitude": row["venue"]["location"]["lng"],
        "Distance": row["venue"]["location"]["distance"]
        }

# Function that takes de API response, cleans it and returns a df
def FromAPIToDF (code, point):
    dicc = APIFoursquare (code, point)
    row = dicc["response"]["groups"][0]["items"]
    lista = list(map(GetLocationData, row))
    df = pd.DataFrame(lista)
    return df


# Function to convert a point into a GeoPoint
def GeoDF(df):
    geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)]
    df2 = pd.DataFrame([])
    crs = {'init': 'epsg:4326'}
    gdf = GeoDataFrame(df2, crs=crs, geometry=geometry)
    return gdf


# Function to calculate the intersection of all areas of interest
def areaPlot2(starbucks_areaB, airport_area, veggie_areaB, school_areaB, irishpub_areaB, conference_areaB, oldcompanies_areaB):
    fig,ax = plt.subplots(figsize= (8,8))
    totarea = 0
    
    for i in starbucks_areaB.index:
        star = PolygonPatch(starbucks_areaB["Area"][i], facecolor='w', edgecolor = "crimson")
        ax.add_patch(star)
        inter = airport_area["Area"][0].intersection(starbucks_areaB["Area"][i])       
            
        for j in veggie_areaB.index:
            veg = PolygonPatch(veggie_areaB["Area"][j], facecolor='w', edgecolor = "#ecf023")
            ax.add_patch(veg)
            inter = inter.intersection(veggie_areaB["Area"][j])           
            
            for k in school_areaB.index:
                pre = PolygonPatch(school_areaB["Area"][k], facecolor='w', edgecolor = "#fe10de")
                ax.add_patch(pre)
                inter = inter.intersection(school_areaB["Area"][k])                
                
                for l in irishpub_areaB.index:
                    irish = PolygonPatch(irishpub_areaB["Area"][l], facecolor='w', edgecolor = "#66ee26")
                    ax.add_patch(irish)
                    inter = inter.intersection(irishpub_areaB["Area"][l])
                                      
                    for m in conference_areaB.index:
                        conf = PolygonPatch(conference_areaB["Area"][m], facecolor='w', edgecolor = "#bf6ae7")
                        ax.add_patch(conf)
                        inter = inter.intersection(conference_areaB["Area"][m])
                        
                        for n in oldcompanies_areaB.index:  
                            old = PolygonPatch(oldcompanies_areaB["Area"][n], facecolor='w', edgecolor = "lightseagreen")
                            ax.add_patch(old)

                            # Difference between Intersection and area of old_companies
                            dif = inter.difference(oldcompanies_areaB["Area"][n])
                            inter = dif

                            if dif:
                                patch = PolygonPatch(dif, facecolor='#f8f65f', edgecolor='#f8f65f')
                                ax.add_patch(patch)
       
                        totarea += dif.area
        
    plt.plot(-410.1, 4486, 'bo')
    plt.xlim(-415,-405)
    plt.ylim(4483,4492)
    plt.xlabel("Longitude (km)", fontsize=12)
    plt.ylabel("Latitude (km)", fontsize=12)
    plt.title("Optimum areas", fontsize=18)
    ax.legend(["My point", "Starbucks", "Veggie", "School", "Irishpub", "Conferences", "Old companies", "Allowed area"])
    plt.show()
    return totarea