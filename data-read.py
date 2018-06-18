#!/usr/bin/python3.5
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from mitemp_bt.mitemp_bt_poller import MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from btlewrap.bluepy import BluepyBackend
import paho.mqtt.client as mqtt
import configparser
import os
import json
import datetime

workdir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read("{0}/devices.ini".format(workdir))

devices = config.sections()

# Init MQTT
mqtt_config = configparser.ConfigParser()
mqtt_config.read("{0}/mqtt.ini".format(workdir))
mqtt_broker_cfg = mqtt_config["broker"]

try:
    mqtt_client = mqtt.Client(mqtt_broker_cfg.get("client"))

    mqtt_username = mqtt_broker_cfg.get("username")
    mqtt_password = mqtt_broker_cfg.get("password")

    if mqtt_username:
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)

    mqtt_client.connect(host=mqtt_broker_cfg.get("host"), port=mqtt_broker_cfg.getint("port"))
except Exception as ex:
    print("Cannot connect to MQTT: {0}".format(str(ex)))
    exit(1)

for device in devices:
    mac = config[device].get("device_mac")
    poller = MiTempBtPoller(mac, BluepyBackend)
    try:
        temperature = poller.parameter_value(MI_TEMPERATURE)
        humidity = poller.parameter_value(MI_HUMIDITY)
        battery = poller.parameter_value(MI_BATTERY)
        json = json.dumps({"temperature": temperature, "humidity": humidity, "battery": battery})
        print(datetime.datetime.now(), device, " : ", json)
        mqtt_client.publish(config[device].get("topic"), json, retain=True)
    except Exception as e:
        print("Error polling device {0}:".format(device))
        print(str(e))
