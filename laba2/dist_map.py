from hazelcast import HazelcastClient
from hazelcast.config import Config
from random import randint


config = Config()
config.cluster_name = 'dev'
config.cluster_members = ['127.0.0.1:5701', '127.0.0.1:5702', '127.0.0.1:5703']
config.client_name = 'MishaPy'
client = HazelcastClient(config=config)
map_ = client.get_map('map')
# for key in range(1000):
#     map_.put(str(key), randint(0, 1000))
client.shutdown()

