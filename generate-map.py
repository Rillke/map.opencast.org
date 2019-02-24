#!/usr/bin/env python3

import sqlite3
import json
from geopy.geocoders import Nominatim

def getUserInformation():
        cacheLocations = []

        geolocator = Nominatim(timeout=10, user_agent='Opencast map generator')

        cur = sqlite3.connect('userTest.db').cursor()
        cur.execute('select distinct country, city, organization from user')
        # DB for, fuer alle Eintraege
        for country, city, organization in cur.fetchall():
            compareCache(country, city, organization)

            #return werte aus compareCache der convert geoJson methode uebergeben
            #geojson.append(compareCache(country, city, organization))
            #request nur in compareCache deswegen hier auslagern!!!!!!!!!!!!
            location = geolocator.geocode({'country': country, 'city': city},
                                        addressdetails=True) \
                    or geolocator.geocode('%s, %s' % (country, city),
                                            addressdetails=True)
            print((country, city), '->', location)

            #wenn formatierung in geocode not None
            if location:
                cacheLocations.append({'country': country,'organization': organization, 'city': city,
                    'latitude': location.latitude, 'longitude': location.longitude})

                yield (location.latitude, location.longitude, organization)
        with open("cache.json", "w") as census:
            census.write(json.dumps(cacheLocations))

def convertGeoJson(addresses):
    features = []
    for lat, lon, org in addresses:
        features.append({
            "type": "Feature",
            "properties": {
                'institution': org,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }})
    return {"type": "FeatureCollection", "features": features}

def compareCache(country, city, organization):
    rt = []

    geolocator = Nominatim(timeout=10, user_agent='Opencast map generator')

    with open('cache.json') as data_file:
        #Speichern des caches in array nicht noetig. Besser mit for cache.json auslesen
        # gefundenen datensatz returnen.
        data = data_file.read(1)
        if data is not None:
            rt = json.load(data_file)
        else:
            print("File is empty")
        check = 0
        for j in range(len(rt)):
            if city == rt[j]['city'] and country == rt[j]['country'] and\
            organization == rt[j]['organization']:
                check = 1
        if check == 1:
            print("im cache vorhanden")
            #hier returnen
        else:
            print("request needed")
            newLocation = geolocator.geocode(country, city, addressdetails=True)
            print(newLocation)
            if newLocation:
                rt.append({"country": country, "city": city, "organization": organization,
                          "latitude": newLocation.latitude, "longitude": newLocation.longitude})
                # datei hinzufuegen, danach returnen der cache positionen

        check = 0;

def main():
    with open("adopters.geojson", "w") as census:
            census.write(json.dumps(convertGeoJson(getUserInformation())))


if __name__ == '__main__':
    main()
