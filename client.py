import threading

import os
import cv2
import json
import requests
from sys import argv
from exceptions import InteropError
from auvsi_suas.proto import interop_api_pb2
from concurrent.futures import ThreadPoolExecutor
from google.protobuf import json_format

filepath=r"C:\Users\Siddharth\Desktop\suas final\interopfile"

class Client(object):
    def __init__(self, url, username, password, max_concurrent=128, max_retries=128):
        self.url = url
        self.username = username
        self.password = password
        self.max_retries = max_retries

        self.lock = threading.Lock()
        self.conn = False
        #self.cookie = None
        self.max_concurrent = 128
        self.session = requests.Session()
        retry_count = 0
        print("check p1")
        params = {"username": self.username, "password": self.password}
        while not self.conn and retry_count < self.max_retries:

            retry_count += 1
            try:
                headers = {"Content-Type": "application/json"}
                params = {"username": self.username, "password": self.password}
                response = self.session.post(self.url + '/api/login', headers=headers, json=params)
                #print(response.headers)

                if response.status_code == 200:
                    print('successfully logged in')
                    self.cookie = response.headers.get('Set-Cookie')
                    self.connection(True)
                    print("cookie:",self.cookie)
                else:
                    print("response status code:{}".format(response.status_code))
            except:
                self.conn = False
                print("error occurred")

        if retry_count >= self.max_retries:
            print("maximum retries reached")

    def connection(self, connect_status):
        self.lock.acquire()
        self.conn = connect_status
        self.lock.release()

    def put_odlc(self, id, odlc):
        response = self.session.post(self.url + '/api/odlcs/image' + id, headers=headers, data=json_data)

        self.status_codes(response.status_code,json_data = json.load(odlc))
        headers = {"Content-Type": "application/json", 'Cookie': self.cookie}
    

    def post_odlc(self):
        
        for i in os.listdir(filepath):
            if i.endswith('json'):
                aa =os.path.join(filepath , i)
                with open(aa , 'r') as fh:
                    #data=fh.read()
                    data = json.load(fh)
                    
                    #print(data)
                headers = {'Cookie': self.cookie}
                response = self.session.post(self.url + '/api/odlcs', headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    print("posted odlc")
                self.status_codes(response.status_code)

    def post_odlc_image(self , id ):

        ii =1
        for i in os.listdir(filepath):

            if i.endswith('png'):
                aa =os.path.join(filepath , i)
               # print(aa)
                with open(aa, 'rb') as f:
                    image_data = f.read()
                    
               

         
                
                headers = {"Content-Type": "image/jpg", 'Cookie': self.cookie}
                response = self.session.post(self.url + '/api/odlcs/' + str(id) + '/image', headers=headers, data=image_data)
                ii+=1  
                if response.status_code == 200:
                    print("image posted sucessfully")
                self.status_codes(response.status_code)
                print(response.status_code)

    def get_mission(self , id ):
        headers = {"Content-Type": "application/json", 'Cookie': self.cookie}
        response = self.session.get(self.url + '/api/missions/' +str(id) ,headers=headers)
        print(response.text)



    def get_odlc_image(self, id):
        headers = {"Content-Type": "application/json", 'Cookie': self.cookie}
        response = self.session.get(self.url + '/api/odlcs/' + str(id) + '/image', headers=headers)
        self.status_codes(response.status_code)
        print(response.text)
        
   

    def get_odlc(self, id):
        headers = {'Cookie': self.cookie}

        response = self.session.get(self.url + '/api/odlcs/' + id, headers=headers)
        odlc = json.loads(response.text)
        self.status_codes(response.status_code)
        return odlc

    def get_odlcs(self, mission_id):
        headers = {'Cookie': self.cookie}
        url = '/api/odlcs'
        if mission_id:
            url += '?mission=%d' % mission_id
        response = self.session.get(self.url + url + '?mission=%d', headers=headers)
        odlcs = []
        for odlc_dict in r.json():
            odlc_proto = interop_api_pb2.Odlc()
            json_format.Parse(json.dumps(odlc_dict), odlc_proto)
            odlcs.append(odlc_proto)
        self.status_codes(response.status_code)
        return odlcs

   

    def status_codes(self, code):

        code = code
        if code == 200:

            print("Successful")

        elif code == 404:
            print("Invalid URL. Check endpoint url.")

        elif code == 403:
            print("Forbidden request")
        elif code == 401:
            print("Unauthorized. Log in and make sure you send cookie")
        elif code == 500:
            print("Internal server error.")
        elif code == 405:
            print("Invalid method.")
        else:
            print("Bad/invalid request")

    def post_telemetry(self, telem):
        params = {'latitude': telem.latitude, 'longtitude': telem.longitude, 'altitude': telem.altitude,
                  'heading': telem.heading}
        headers = {"Content-Type": "application/json"}
        response = self.session.post(self.url + '/api/telemetry', headers=headers,
                                     data=json_format.MessageToJson(telem))

        if response.status_code == 200:
            print("posted telemetry")
        self.status_codes(response.status_code)


class AsyncClient(object):

    def __init__(self,
                 url,
                 username,
                 password,
                 max_concurrent=128,
                 max_retries=10):
        self.client = Client(url, username, password, max_concurrent,
                             max_retries)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    def get_teams(self):
        return self.executor.submit(self.client.get_teams)

    def get_mission(self, mission_id):
        return self.executor.submit(self.client.get_mission, mission_id)

    def post_telemetry(self, telem):
        return self.executor.submit(self.client.post_telemetry, telem)

    def get_odlcs(self, mission=None):
        return self.executor.submit(self.client.get_odlcs, mission)

    def get_odlc(self, odlc_id):
        return self.executor.submit(self.client.get_odlc, odlc_id)

    def post_odlc(self):
        return self.executor.submit(self.client.post_odlc)

    def put_odlc(self, odlc_id, odlc):
        return self.executor.submit(self.client.put_odlc, odlc_id, odlc)

    def delete_odlc(self, odlc_id):
        return self.executor.submit(self.client.delete_odlc, odlc_id)

    def get_odlc_image(self, odlc_id):
        return self.executor.submit(self.client.get_odlc_image, odlc_id)

    def post_odlc_image(self,odlc_id,image_data):
        return self.executor.submit(self.client.post_odlc_image, odlc_id,image_data)

    def delete_odlc_image(self, odlc_id):
        return self.executor.submit(self.client.delete_odlc_image, odlc_id)

    def mission_statob(self,odlc_id):
        return self.executor.submit(self.client.mission_statob,odlc_id)
    print("done")


