#!/usr/bin/python3
# publisher

#required libraries for mqtt and AWS IoT
import sys
import ssl
import json
import paho.mqtt.client as mqtt
from sys import argv
import zbar
from PIL import Image
import time
from datetime import datetime
import RPi.GPIO as GPIO
#creating a client with client-id=mqtt-test
#mqttc = mqtt.Client(client_id="test")
mqttc = mqtt.Mosquitto()

#Configure network encryption and authentication options. Enables SSL/TLS support.
#adding client-side certificates and enabling tlsv1.2 support as required by aws-iot service
mqttc.tls_set(ca_certs="/etc/mosquitto/certs/ca.crt",
                    certfile="/etc/mosquitto/certs/server.crt",
                    keyfile="/etc/mosquitto/certs/server.key",
                tls_version=ssl.PROTOCOL_TLSv1,
                ciphers=None)
mqttc.username_pw_set('atns', 'rasp')

mqttc.connect("192.168.43.143",8883)


# start a new thread handling communication with AWS IoT
mqttc.loop_start()

try:
	if len(argv) < 2: exit(1)

	# create a reader
	scanner = zbar.ImageScanner()

	# configure the reader
	scanner.parse_config('enable')

	# obtain image data
	if(argv[1] == "EOInput"):
                payload = str("EOInput")
                msg_info = mqttc.publish("test", payload, qos=1)
        else:
                pil = Image.open(argv[1]).convert('L')
                width, height = pil.size
                raw = pil.tobytes()

                # wrap image data
                image = zbar.Image(width, height, 'Y800', raw)

                # scan the image for barcodes
                scanner.scan(image)
                if(len(argv) < 3):
                        quant = 0
                else:
                        quant = argv[2]
                # extract results
                for symbol in image:
                        # do something useful with results
                        payload =  symbol.data + "," + str(quant)
                        msg_info = mqttc.publish("test", payload, qos=1)

                # clean up
                del(image)

except KeyboardInterrupt:
    pass

GPIO.cleanup()
