from auvsi_suas.client import client
from auvsi_suas.proto import interop_api_pb2


'''
client = client.Client(url='http://13.59.159.169:8000',
                       username='testuser',
                       password='testpass')
print("connected")
#client.get_mission(1)
'''
client = client.Client
client.post_odlc_image()
#client.get_odlc_image(16)
#client.post_odlc()

'''

teams = client.get_teams()
print(teams)

get(url , user)

mission = client.get_mission(1)
print(mission)


client.post_telemetry(telemetry)


odlc = client.post_odlc(odlc)

with open('path/to/image/A.jpg', 'rb') as f:
    image_data = f.read()
    client.put_odlc_image(odlc.id, image_data)
'''