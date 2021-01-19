import logging
import json
import os
import azure.functions as func
from arcgis.features.manage_data import dissolve_boundaries
from arcgis.features.find_locations import find_centroids
from arcgis.geometry import from_geo_coordinate_string
from arcgis.geocoding import geocode
from arcgis.geometry import lengths, areas_and_lengths, project
from arcgis.geometry import Point, Polyline, Polygon, Geometry
from arcgis.gis import GIS
import arcgis
from arcgis import geometry 
from arcgis import features
from arcgis.geoanalytics import manage_data
from arcgis.features.manage_data import overlay_layers
from arcgis.features import GeoAccessor, GeoSeriesAccessor, FeatureLayer
from arcgis.features import FeatureLayerCollection
import pandas


def main(msg: func.QueueMessage, msg1: func.Out[str]) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    
    test = os.environ["testers"]#Read keyvault credentials integrated in the function
    gis = GIS("https://yyyy.maps.arcgis.com", "UserName", test)#Log into ESRI Portal with the password read above
    #Delete following feature Services if found.
    try:
        gis.content.search("nffindcentroids")[0].delete()
        gis.content.search("nfHealthLyrPolygonToPoint")[0].delete()
    except:
        pass
    #Download fc with the following ID
    item=gis.content.get('asset 2 FeatureServiceID')#Find asset2 feature service using the given feature service ID
    l=item.layers[0]#Create a layer
    dissolve_fields=['LOIS']#List of Fields to dissolve on
    try:
        g=dissolve_boundaries(l, dissolve_fields,output_name='nffindcentroids')#Dissolve the polygon feature service on these fields
        #Dissolve downloaded feature service into multipart polygon and save on portal as 'findcentroids' and get the new feature's ID
        c= gis.content.get(g.id).layers[0]#Create Layer for feature published above
    except:
        pass
     #Calculate the new feature ID's Centroids an save resulting point feature servic on Portal as HealthLyrPolygonToPoint
    try:
        pp= find_centroids(c, output_name="nfHealthLyrPolygonToPoint")
        tableNF= gis.content.get(pp.id).layers[0].query().sdf
        msg1.set(msg.get_body().decode('utf-8'))#write message used to trigger this function in new queue
    except:
        pass
    