# TrackCTABus.py

import urllib
from xml.etree.ElementTree import fromstring
import time
import webbrowser

target_latitude = 41.980262


suitcase_busses = {'4067'}


def distance(lat1, lat2):
    'Return approx miles between lat1 and lat2'
    return 69 * abs(lat1 - lat2)


def check():
    httpRequest = urllib.urlopen('http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22')

    # write the data to the file
    xmlDataString = httpRequest.read()
    phile = open('rt22.xml', 'wb')
    phile.write(xmlDataString)
    phile.close
    print('Bus information updated.')

    # parse the data appropriately
    doc = fromstring(xmlDataString)
    for every_bus in doc.findall('bus'):
        busId = every_bus.findtext('id')
        if busId in suitcase_busses:
            latitude = float(every_bus.findtext('lat'))
            longitude = float(every_bus.findtext('lon'))
            distanceFromOffice = distance(latitude, target_latitude)
            direction = every_bus.findtext('d')
            print('%s %s %0.2f miles' % (busId, direction, distanceFromOffice))
            if distanceFromOffice < .5:
                # Launch a browser to see on a map
                webbrowser.open('http://maps.googleapis.' +
                'com/maps/api/staticmap?size=500x500&sensor' +
                '=false&markers=|%f,%f' % (latitude, longitude))


while True:
    check()
    time.sleep(60)
