# About
This is simple python script, which scans Xiaomi BLE Temperature and Humidity sensors and publishes measurements to MQTT. 

# Installation

1.Install required packages:

    sudo pip3 install mitemp_bt
    sudo pip3 install bluepy
    sudo pip3 install paho-mqtt

2.Clone code:

    git clone https://github.com/algirdasc/xiaomi-ble-mqtt.git
    cd xiaomi-ble-mqtt

3.Add crontab task. Task will be run every 5 minutes:

    crontab -e
	# Add row
	*/5 * * * * /usr/bin/python3.5 <path to xiaomi-ble-mqtt>/data-read.py >> <path to xiaomi-ble-mqtt>/xiaomi-ble.log 2>&1

4.Configure MQTT broker by editing `mqtt.ini` file.

5.Scan for available Xiaomi BLE devices:

     sudo hcitool lescan

Look for line which looks like this: 

    4C:65:A8:D4:A3:1D MJ_HT_V1

5.Configure Xiaomi devices by editing devices.ini file:

    [room1]
    device_mac=4C:65:A8:XX:XX:XX
    topic=sensors/room1
    availability_topic=sensors/room1/availability
    average=3
    
    [room2]
    device_mac=4C:65:A8:XX:XX:XX
    topic=sensors/room2
    
    etc...

MQTT Payload example:

    {"temperature": 25.7, "humidity": 42.0, "battery": 100}

