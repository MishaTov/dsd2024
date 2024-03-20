from hazelcast import HazelcastClient
from hazelcast.config import Config
from time import sleep


def on_message(topic_message):
    sleep(3)
    print(f'Received: {topic_message.message}')


config = Config()
config.cluster_name = 'dev'
config.cluster_members = ['127.0.0.1:5701', '127.0.0.1:5702', '127.0.0.1:5703']
config.client_name = 'MishaPy'
client = HazelcastClient(config=config)
topic = client.get_topic('topic').blocking()
topic.add_listener(on_message)

input('(Sub 1) Press any key to exit\n')

client.shutdown()

