import paho.mqtt.client as mqtt
from analyze import ocr, parse
import cv2
import json
import argparse
import time
from picamera2 import Picamera2
import threading 
import queue
import collections


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

class Worker(threading.Thread): 
    def __init__(self, q: queue.Queue): 
        threading.Thread.__init__(self, daemon=True)
        self.q = q
        # helper function to execute the threads
    def run(self):         
        prev = 0
        start = False
        while True:
            img_orig = self.q.get()
            if img_orig is None:
                start = True                
                consumptions = []
                continue
            if not start:
                continue
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
            time.sleep(0)
            if err:
                continue
            consumptions.append(consumption)
            consumption, count = collections.Counter(consumptions).most_common(1)[0]
            if count < 3:
                continue
            consumption = consumption / 10
            if True: #0 <= (consumption-prev) < 500:
                data = json.dumps(dict(volume=consumption))
                print('publish', not args.nopublish, data)
                if not args.nopublish:
                    client.publish("neptune/status", data)
            prev = consumption
            start = False



# The callback for when a PUBLISH message is received from the server.
def on_message(client, q, msg):

    t0 = time.time()
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1640, 1232)}))
    picam2.start()
    q.put(None)  
    while time.time() - t0 < 15:
        img_orig = picam2.capture_array()
        q.put(img_orig)
        time.sleep(0)
    picam2.stop()
    picam2.close()
    

q = queue.Queue()
Worker(q).start()
client = mqtt.Client(userdata=q)
client.on_connect = on_connect
client.on_message = on_message
client.connect("nas.home.arpa")
client.loop_forever()
