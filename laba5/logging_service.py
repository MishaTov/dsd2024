from flask import Flask, request
import hazelcast
import argparse
import os
import subprocess
import threading
import consul
from uuid import uuid4


app = Flask(__name__)


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


def start_hz():
    cur_path = os.environ.get('PATH', '')
    hz_path = r'F:\hz\hazelcast-5.3.0\bin'
    os.environ['PATH'] = f'{hz_path};{cur_path}'
    return subprocess.run('hz-start.bat', shell=True)


def get_service_urls(service_name):
    return list(map(lambda x: f"{x['ServiceAddress']}:{x['ServicePort']}", c.catalog.service(service_name)[1]))


def reg_service(address_, port_):
    existing_urls = get_service_urls('facade service') + get_service_urls('logging service') + \
                    get_service_urls('messages service')
    if f'{address_}:{port_}' not in existing_urls:
        c.agent.service.register(name='logging service',
                                 service_id=str(uuid4()),
                                 address=address_,
                                 port=port_)


def get_hz_map():
    return c.kv.get('hz map')[1]['Value'].decode()


def put_message(client, uuid, message):
    messages = client.get_map(hz_map).blocking()
    messages.put(uuid, message)


def get_messages(client):
    messages = client.get_map(hz_map).blocking()
    return ', '.join(messages.values())


@app.route('/', methods=['GET', 'POST'])
def response():
    with HazelcastClient() as client:
        if request.method == 'GET':
            messages = get_messages(client)
            return messages
        elif request.method == 'POST':
            uuid, msg = request.form['uuid'], request.form['msg']
            put_message(client, uuid, msg)
            print(f'New record:\n\tuuid: {uuid}\n\ttext: {msg}')
            return 'Success'


if __name__ == '__main__':
    address, port = start()
    c = consul.Consul()
    reg_service(address, port)
    hz_map = get_hz_map()
    app_ = threading.Thread(target=app.run, kwargs={'host': address, 'port': port,
                                                    'debug': True, 'use_reloader': False})
    hz = threading.Thread(target=start_hz)
    app_.start()
    hz.start()

