from flask import Flask
import hazelcast
import argparse
import consul
from uuid import uuid4


app = Flask(__name__)

messages = []


class HazelcastClient:

    def __enter__(self):
        self.client = hazelcast.HazelcastClient()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.shutdown()


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--address', default='127.0.0.1')
    args = parser.parse_args()
    return args.address, args.port


def get_service_urls(service_name):
    return list(map(lambda x: f"{x['ServiceAddress']}:{x['ServicePort']}", c.catalog.service(service_name)[1]))


def reg_service(address_, port_):
    existing_urls = get_service_urls('facade service') + get_service_urls('logging service') + \
                    get_service_urls('messages service')
    if f'{address_}:{port_}' not in existing_urls:
        c.agent.service.register(name='messages service',
                                 service_id=str(uuid4()),
                                 address=address_,
                                 port=port_)


def get_hz_queue():
    return c.kv.get('hz queue')[1]['Value'].decode()


def message_added(event):
    last_message = event.item
    messages.append(last_message)
    print(f'Received message: {last_message}')
    msg_queue.remove(last_message)


@app.route('/', methods=['GET'])
def get_message():
    return ', '.join(messages)


if __name__ == '__main__':
    address, port = start()
    c = consul.Consul()
    reg_service(address, port)
    with HazelcastClient() as client:
        msg_queue = client.get_queue(get_hz_queue())
        msg_queue.add_listener(include_value=True, item_added_func=message_added)
        app.run(host=address, port=port, debug=True)
