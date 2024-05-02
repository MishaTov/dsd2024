import requests
from flask import Flask, request
from uuid import uuid4
from random import choice
import hazelcast
import argparse
import consul


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


def get_service_urls(service_name):
    return list(map(lambda x: f"http://{x['ServiceAddress']}:{x['ServicePort']}", c.catalog.service(service_name)[1]))


def reg_service(address_, port_):
    existing_urls = get_service_urls('facade service') + get_service_urls('logging service') + \
                    get_service_urls('messages service')
    if f'http://{address_}:{port_}' not in existing_urls:
        c.agent.service.register(name='facade service',
                                 service_id=str(uuid4()),
                                 address=address_,
                                 port=port_)


def set_hz_map():
    if not c.kv.get('hz map')[1]:
        c.kv.put('hz map', 'messages')


def get_hz_queue():
    if not c.kv.get('hz queue')[1]:
        c.kv.put('hz queue', 'messages')
    return c.kv.get('hz queue')[1]['Value'].decode()


def check_available_service():
    available_log_services, available_msg_services = [], []
    for url in get_service_urls('logging service'):
        try:
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                available_log_services.append(url)
        except (requests.ConnectionError, requests.ReadTimeout):
            continue
    for url in get_service_urls('messages service'):
        try:
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                available_msg_services.append(url)
        except (requests.ConnectionError, requests.ReadTimeout):
            continue
    return available_log_services, available_msg_services


@app.route('/', methods=['GET', 'POST'])
def handler():
    log_service_urls, msg_service_urls = check_available_service()
    if not log_service_urls or not msg_service_urls:
        return '<h1>Services are not available</h1>', 503
    with HazelcastClient() as client:
        if request.method == 'GET':
            return f'from logging service: {requests.get(choice(log_service_urls)).text} <p>' \
                   f'from messages service: {requests.get(choice(msg_service_urls)).text}'
        elif request.method == 'POST':
            msg = request.form['msg']
            data = {'uuid': str(uuid4()), 'msg': msg}
            msg_queue = client.get_queue(hz_queue).blocking()
            msg_queue.offer(msg)
            return requests.post(choice(log_service_urls), data=data).text


if __name__ == '__main__':
    address, port = start()
    c = consul.Consul()
    reg_service(address, port)
    set_hz_map()
    hz_queue = get_hz_queue()
    app.run(host=address, port=port, debug=True)
