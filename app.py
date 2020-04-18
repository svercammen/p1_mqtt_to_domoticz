import base64
import json
import os
import sys
import urllib

from paho.mqtt import subscribe


def get_environment_variable(name):
    if name in os.environ:
        return os.environ[name]
    else:
        print(f"Environment variable {name} is not set. Exiting.")
        sys.exit(1)


MQTT_HOST = get_environment_variable("mqtt_host")
MQTT_PORT = int(get_environment_variable("mqtt_port"))
MQTT_TOPIC = get_environment_variable('mqtt_topic')

POWER_IDX = get_environment_variable('power_idx')
GAS_IDX = get_environment_variable('gas_idx')

DOMOTICZ_HOST = get_environment_variable('domoticz_host')
DOMOTICZ_PORT = get_environment_variable('domoticz_port')
DOMOTICZ_USERNAME = get_environment_variable('domoticz_username')
DOMOTICZ_PASSWORD = get_environment_variable('domoticz_password')


def on_message(client, userdata, message):
    print(f"got message: {message.payload}")

    payload = json.loads(message.payload)

    kwh_high = payload['kwh_high'] * 1000
    kwh_low = payload['kwh_low'] * 1000
    kwh_current = payload['kwh_current'] * 1000
    kwh_return_high = 0
    kwh_return_low = 0
    kwh_return_current = 0

    authorization_header = base64.encodebytes(('%s:%s' % (DOMOTICZ_USERNAME, DOMOTICZ_PASSWORD)).encode()) \
        .decode() \
        .replace('\n', '')

    uri = f"http://{DOMOTICZ_HOST}:{DOMOTICZ_PORT}/json.htm?type=command&param=udevice&idx={POWER_IDX}&nvalue=0&" \
          f"svalue={kwh_high};{kwh_low};{kwh_return_high};{kwh_return_low};{kwh_current};{kwh_return_current}"
    request = urllib.request.Request(uri)
    request.add_header("Authorization", "Basic %s" % authorization_header)
    urllib.request.urlopen(request)

    gas = payload['gas'] * 1000
    uri = f"http://{DOMOTICZ_HOST}:{DOMOTICZ_PORT}/json.htm?type=command&param=udevice&idx={GAS_IDX}&nvalue=0&svalue={gas}"
    request = urllib.request.Request(uri)
    request.add_header("Authorization", "Basic %s" % authorization_header)
    urllib.request.urlopen(request)

print("connecting to MQTT on {}:{}".format(MQTT_HOST, MQTT_PORT))
subscribe.callback(on_message, MQTT_TOPIC, hostname=MQTT_HOST, port=MQTT_PORT)
