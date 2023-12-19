import paho.mqtt.client as mqtt
from analyze import ocr, parse
import cv2
import json
import argparse
import shlex
import tempfile
import subprocess
import time
from collections import Counter


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
    client.subscribe("neptune/ping")


prev = 0
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    t0 = time.time()
    consumptions = []
    while time.time() - t0 < 30:
        with tempfile.NamedTemporaryFile(suffix='.jpeg') as tmp:
            img_file = tmp.name
            subprocess.check_output(shlex.split(f'libcamera-jpeg -n -t 1 -o {img_file}'), stderr=subprocess.DEVNULL)
            img_orig = cv2.imread(img_file)
            img_orig = cv2.rotate(img_orig, cv2.ROTATE_180)
            img = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
            ocr_err, result, _ = ocr(img)
            parse_err, consumption = parse(result)
            err = ocr_err or parse_err
            print('err', err, 'consumption', consumption)
            if not err:
                consumptions.append(consumption)        
                (consumption, count) = Counter(consumptions).most_common(1)
                if count > 3:
                    break
    
    filename = f'data/{result}.png'
    print('err:', err, 'result:', result, filename)
    if args.dump or (err and args.dump_err):
        cv2.imwrite(filename, img)
    if err:
        return
    global prev
    consumption = consumption / 10
    if True: #0 <= (consumption-prev) < 500:
        data = json.dumps(dict(volume=consumption))
        print('publish', not args.nopublish, data)
        if not args.nopublish:
            client.publish("neptune/status", data)
    prev = consumption


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("nas.home.arpa")
client.loop_forever()
