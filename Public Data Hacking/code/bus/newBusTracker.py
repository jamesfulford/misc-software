# TrackCTABus.py
# Use this to listen to data on:
    # Busses in Chicago
# by James Fulford
# Began: 6/7/2016
# Stopped Developing:


import urllib
from xml.etree.ElementTree import fromstring
import time
import webbrowser


# TODO make a class of pertinent information, have it be passed around in listen
class information:
    target_latitude = 41.980262
    suitcase_busses = {'4067'}
    cta_bus_link = 'http://ctabustracker.com/bustime/map/' + \
                   'getBusesForRoute.jsp?route=22'
    tolerance = .5

allInformation = information()




def listen(busses, target_coordinates, tolerance, timeout_seconds, weblink):
    stillLost = True
    saveData('rt22.xml', weblink)
    while stillLost:
        if applies(busses, target_coordinates, tolerance):
            report(busses, target_coordinates, tolerance)
            break
        time.sleep(timeout_seconds)


def saveData(filepath, website):
    httpRequest = urllib.urlopen(website)
    xmlDataString = httpRequest.read()
    phile = open(filepath, "wb")
    phile.write(xmlDataString)
    phile.close()
    print('Data updated.')


def applies(busses, target_coordinates, tolerance):
    """
    Every time we ping for data, return whether to act or not
    """
    doc = getXMLTreeFromInternet()
    for every_bus in doc.findall('bus'):
        busId = every_bus.findtext('id')
        if busId in busses:
            latitude = float(every_bus.findtext('lat'))
            longitude = float(every_bus.findtext('lon'))
            distanceFromOffice = distance(latitude, target_coordinates[0])
            direction = every_bus.findtext('d')
            print('%s %s %0.2f miles' % (busId, direction, distanceFromOffice))
            if distanceFromOffice < tolerance:
                return True
    return False


def report(bus_coordinates, target_coordinates, tolerance):
    """
    Runs whenever applies method evaluates to true.
    """
    print("Bus within " + str(tolerance) + " of target.")
    webbrowser.open('http://maps.googleapis.' +
                    'com/maps/api/staticmap?size=500x500&sensor' +
                    '=false&center=%f,%f&markers=%f,%f&markers=color:blue|%f,%f' %  # test
                    (target_coordinates[0], target_coordinates[1],
                     target_coordinates[0], target_coordinates[1],
                     bus_coordinates[0], bus_coordinates[1]))


"""
Below is all the helper methods
"""


def getXMLTreeFromInternet():
    httpRequest = urllib.urlopen('http://ctabustracker.com/' +
                                 'bustime/map/getBusesForRoute.jsp?route=22')
    xmlDataString = httpRequest.read()

    return fromstring(xmlDataString)


def distance(bus_coordinates, target_coordinates):
    'Return approx miles between lat1 and lat2'
    return 69 * abs(bus_coordinates[0] - target_coordinates[0])


def googleMaps(center, markers):
    """
    Provided a tuple with latitude, longitude of the center of the map
    and a list of tuples specifying latitude, longitude, then color(optional)
    opens a google map static image of dimensions 500x500.
    """
    url = 'http://maps.googleapis.com/maps/api/' + \
          'staticmap?size=500x500&sensor=false'
    url = url + 'center=%f,%f' % (center[0], center[1])
    if len(markers) == 1:
        if len(markers[0]) == 2:
            url = url + '&markers=%f,%f' % (markers[0][0], markers[0][1])
        elif len(markers[0]) == 3:
            url = url + '&markers=color:%s|%f,%f' % \
                (markers[0][2], markers[0][0], markers[0][1])
    else:
        for marker in markers:
            if len(marker) == 2:
                url = url + '&markers=%f,%f' % (marker[0], marker[1])
            elif len(marker) == 3:
                url = url + '&markers=color:%s|%f,%f' % \
                    (marker[2], marker[0], marker[1])
    webbrowser.open(url)






