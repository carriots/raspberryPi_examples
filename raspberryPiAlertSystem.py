#-*-coding:utf8-*-
"""
    Carriots.com
    Created 11 Jan 2013
    Revised 15 Apr 2014

    This sketch sends streams to Carriots according to the values read by a LDR sensor
"""

import RPi.GPIO as GPIO
from urllib2 import urlopen, Request
from time import mktime, sleep
from datetime import datetime
from json import dumps


class Client (object):
    api_url = "http://api.carriots.com/streams"

    def __init__(self, api_key=None, client_type='json'):
        self.client_type = client_type
        self.api_key = api_key
        self.content_type = "application/vnd.carriots.api.v2+%s" % self.client_type
        self.headers = {'User-Agent': 'Raspberry-Carriots',
                        'Content-Type': self.content_type,
                        'Accept': self.content_type,
                        'Carriots.apikey': self.api_key}
        self.data = None
        self.response = None

    def send(self, data):
        self.data = dumps(data)
        request = Request(Client.api_url, self.data, self.headers)
        self.response = urlopen(request)
        return self.response


def rc_time(pipin):
    measurement = 0
    GPIO.setup(pipin, GPIO.OUT)
    GPIO.output(pipin, GPIO.LOW)
    sleep(0.1)

    GPIO.setup(pipin, GPIO.IN)

    while GPIO.input(pipin) == GPIO.LOW:
        measurement += 1

    return measurement


def main():
    GPIO.setmode(GPIO.BCM)

    on = 1  # Constant to indicate that lights are on
    off = 2  # Constant to indicate that lights are off

    device = "YOUR DEVICE's ID_DEVELOPER HERE"  # Replace with the id_developer of your device
    apikey = "YOUR APIKEY HERE"  # Replace with your Carriots apikey

    lights = off  # Current status

    client_carriots = Client(apikey)

    # The loop routine runs over and  over again forever
    while True:
        timestamp = int(mktime(datetime.utcnow().timetuple()))
        print rc_time(4)
        # This is the value limit between day or night with or LDR sensor and our capacitor.
        # Maybe you need adjust this value.
        if rc_time(4) > 600:
            new_lights = off
            print("Lights OFF")
        else:
            new_lights = on
            print("Lights ON")

        if lights is not new_lights:  # Check if we have a change in status
            lights = new_lights  # Status update and send stream
            data = {"protocol": "v2", "device": device, "at": timestamp, "data": dict(
                light=("ON" if new_lights is on else "OFF"))}
            carriots_response = client_carriots.send(data)
            print carriots_response.read()


if __name__ == '__main__':
    main()
