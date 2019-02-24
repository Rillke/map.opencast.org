#!/usr/bin/env python3

import sqlite3
import json
from geopy.geocoders import Nominatim
import os

def getUserInformation():
        locations = []

        geolocator = Nominatim(timeout=10, user_agent='Opencast map generator')

        cur = sqlite3.connect('userTest.db').cursor()
        cur.execute('select distinct country, city, organization from user')
        # DB for, fuer alle Eintraege
        for country, city, organization in cur.fetchall():
            locations.append(compareCache(country, city, organization))
        return locations

         

def convertGeoJson(addresses):
    features = []
    for i in addresses:
        features.append({
            "type": "Feature",
            "properties": {
                'institution': i["organization"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [i["longitude"], i["latitude"]]
            }})
    return {"type": "FeatureCollection", "features": features}

def compareCache(country, city, organization):

    geolocator = Nominatim(timeout=10, user_agent='Opencast map generator')
    check = 0
    with open('cache.json') as data_file:
        if os.stat("cache.json").st_size == 0:
            newLocation = geolocator.geocode(country, city, addressdetails=True) or geolocator.geocode('%s, %s' % (country, city),addressdetails=True)
            #print(newLocation)
            if newLocation:
                data = []
                os.remove("cache.json")
                f = open("cache.json","a")
                geoLocation = {"country": country, "city": city, "organization": organization,
                    "latitude": newLocation.latitude, "longitude": newLocation.longitude}
                data.append(geoLocation)
                f.write(json.dumps(data))
                return geoLocation
        else:
            data = json.load(data_file)
            for item in data:
                #print(item)
                if city == item["city"] and country == item['country'] and organization == item['organization']:
                    check = 1
                    if check == 1:
                        print("im cache vorhanden")
                        return item
            else:
                print("request done")
                newLocation = geolocator.geocode(country, city, addressdetails=True) or geolocator.geocode('%s, %s' % (country, city),addressdetails=True)
                #print(newLocation)
                if newLocation:
                    os.remove("cache.json")
                    f = open("cache.json","a")
                    geoLocation = {"country": country, "city": city, "organization": organization,
                        "latitude": newLocation.latitude, "longitude": newLocation.longitude}
                    data.append(geoLocation)
                    f.write(json.dumps(data))
                    return geoLocation
            check = 0

def main():
    with open("adopters.geojson", "w") as census:
            census.write(json.dumps(convertGeoJson(getUserInformation())))


if __name__ == '__main__':
    main()
