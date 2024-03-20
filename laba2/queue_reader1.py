from hazelcast import HazelcastClient
from hazelcast.config import Config
from time import sleep


config = Config()
config.cluster_name = 'dev'
config.cluster_members = ['127.0.0.1:5701', '127.0.0.1:5702', '127.0.0.1:5703']
config.client_name = 'MishaPy'
client = HazelcastClient(config=config)
queue = client.get_queue('queue').blocking()
taken_items = []
while True:
    sleep(0.3)
    item = queue.poll()
    if item is None:
        break
    taken_items.append(item)
print(f'Items taken by reader 1: \n{taken_items}\n'
      f'Total taken count: {len(taken_items)}')
client.shutdown()

