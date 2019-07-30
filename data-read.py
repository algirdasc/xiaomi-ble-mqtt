#!/usr/bin/python3.5
from mitemp.mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from mitemp_bt.mitemp_bt_poller import MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from btlewrap.bluepy import BluepyBackend
from bluepy.btle import BTLEException
import paho.mqtt.client as mqtt
import traceback
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

# Averages
averages = configparser.ConfigParser()
averages.read("{0}/averages.ini".format(workdir))

for device in devices:

    mac = config[device].get("device_mac")
    poller = MiTempBtPoller(mac, BluepyBackend, ble_timeout=config[device].getint("timeout", 10))

    try:

        temperature = poller.parameter_value(MI_TEMPERATURE)
        humidity = poller.parameter_value(MI_HUMIDITY)
        battery = poller.parameter_value(MI_BATTERY)

        data = json.dumps({
            "temperature": temperature,
            "humidity": humidity,
            "battery": battery
        })

        # Check averages
        avg = []
        average_count = config[device].getint("average")
        if average_count:
            if mac in averages.sections():
                avg = json.loads(averages[mac]["avg"])

            # Add average
            avg.insert(0, data)

            # Strip data
            avg = avg[0:average_count]

            # Calc averages
            temperature = 0
            humidity = 0
            battery = 0

            for a in avg:
                al = json.loads(a)
                temperature += al["temperature"]
                humidity += al["humidity"]
                battery += al["battery"]

            temperature = round(temperature / len(avg), 1)
            humidity = round(humidity / len(avg), 1)
            battery = round(battery / len(avg), 1)

            # Convert averages
            averages[mac] = {}
            averages[mac]["avg"] = json.dumps(avg)

            # Rewrite data
            data = json.dumps({
                "temperature": temperature,
                "humidity": humidity,
                "battery": battery,
                "average": len(avg)
            })

        print(datetime.datetime.now(), device, " : ", data)

        mqtt_client.publish(config[device].get("topic"), data, retain=config[device].getboolean("retain", False))
        mqtt_client.publish(config[device].get("availability_topic"), "online")
    except BTLEException as e:
        mqtt_client.publish(config[device].get("availability_topic"), "offline")
        print("Error connecting to device {0}: {1}".format(device, str(e)))
    except Exception as e:
        mqtt_client.publish(config[device].get("availability_topic"), "offline")
        print("Error polling device {0}:".format(device))
        print(traceback.print_exc())

with open("{0}/averages.ini".format(workdir), "w") as averages_file:
    averages.write(averages_file)

mqtt_client.disconnect()
