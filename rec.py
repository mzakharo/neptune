import paho.mqtt.client as mqtt
from analyze import ocr, parse
import cv2
import json
import argparse
import time
from picamera2 import Picamera2



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
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1640, 1232)}))
    picam2.start()
    try:
        while time.time() - t0 < 30:
            img_orig = picam2.capture_array()

            tx = time.time()
            img_orig_rot = cv2.rotate(img_orig, cv2.ROTATE_180)
            img = cv2.cvtColor(img_orig_rot, cv2.COLOR_BGR2GRAY)
            try: 
                ocr_err, result, _ = ocr(img)
            except Exception as e:
                print(e)
                ocr_err = True
                result = 'ocr_exception'
            parse_err, consumption = parse(result)
            tt = time.time() - tx
            err = ocr_err or parse_err
            filename = f'data/{result}.jpeg'
            print('err:', err, 'result:', result, filename, 'took', tt)
            if args.dump or (err and args.dump_err):
                cv2.imwrite(filename, img_orig)
            if not err:
                break
    finally:
        picam2.stop()
        picam2.close()
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
