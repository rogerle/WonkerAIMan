import requests
import json
import cv2
import base64

import numpy as np

def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')

def base64_to_cv2(b64str):
    data = base64.b64decode(b64str.encode('utf8'))
    data = np.fromstring(data, np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return data

org_im = cv2.imread('/home/rogerle/PycharmProjects/WonkerAIMan/data/test/2.jpg')

data = {'images':[cv2_to_base64(org_im)],'top_k':2}
headers = {"Content-type": "application/json"}
url = "http://127.0.0.1:8866/predict/resnet50_vd_imagenet_ssld"
r = requests.post(url=url, headers=headers, data=json.dumps(data))
data =r.json()['results']['data']

if data[0].get('0') > 0.8:
    print("match")
else:
    print("not match")

data2 = {'images':[cv2_to_base64(org_im)]}
headers = {"Content-type": "application/json"}
url = "http://127.0.0.1:8866/predict/pyramidbox_lite_server"
r = requests.post(url=url, headers=headers, data=json.dumps(data2))

print(r.json())