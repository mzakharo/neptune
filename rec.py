import paho.mqtt.client as mqtt
from analyze import ocr, parse
import cv2
import json
import argparse
import time
import numpy as np
import collections
MQTT_TOPIC = "esp32/cam/image"

parser = argparse.ArgumentParser()
parser.add_argument('--dump', action='store_true')
parser.add_argument('--dump_err', action='store_true')
parser.add_argument('--nopublish', action='store_true')
args = parser.parse_args()

print('args', args)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    image_data = msg.payload
    print(f"Received image data of size: {len(image_data)} bytes")

    np_array = np.frombuffer(image_data, np.uint8)
                
    # Decode the image using OpenCV
    img_orig = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
 

    img_orig_rot = cv2.rotate(img_orig, cv2.ROTATE_180)
    img = cv2.cvtColor(img_orig_rot, cv2.COLOR_BGR2GRAY)
    try: 
        ocr_err, result, _ = ocr(img)
    except Exception as e:
        print(e)
        ocr_err = True
        result = 'ocr_exception'
    parse_err, consumption = parse(result)
    err = ocr_err or parse_err
    filename = f'data/{result}.jpeg'
    print('err:', ocr_err, 'parse', parse_err, 'result:', result, filename)
    if args.dump or (err and args.dump_err):
        cv2.imwrite(filename, img_orig)
    if err:
        return
    consumption = consumption / 10
    if True: #0 <= (consumption-prev) < 500:
        data = json.dumps(dict(volume=consumption))
        print('publish', not args.nopublish, data)
        if not args.nopublish:
            client.publish("neptune/status", data)
    prev = consumption
    
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("nas.local")
client.loop_forever()
print('exit')
