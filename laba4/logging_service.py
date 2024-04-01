from flask import Flask, request
from hazelcast import HazelcastClient
import argparse
import os
import subprocess
import threading


parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
args = parser.parse_args()

app = Flask(__name__)


def start_app():
    return app.run(debug=True, use_reloader=False, port=args.port)


def start_hz():
    cur_path = os.environ.get('PATH', '')
    hz_path = r'F:\hz\hazelcast-5.3.0\bin'
    os.environ['PATH'] = f'{hz_path};{cur_path}'
    return subprocess.run('hz-start.bat', shell=True)


def put_message(client, uuid, message):
    messages = client.get_map('messages').blocking()
    messages.put(uuid, message)


def get_messages(client):
    messages = client.get_map('messages').blocking()
    return ', '.join(messages.values())


@app.route('/', methods=['GET', 'POST'])
def response():
    if request.method == 'GET':
        client = HazelcastClient()
        return get_messages(client)
    elif request.method == 'POST':
        uuid, msg = request.form['uuid'], request.form['msg']
        client = HazelcastClient()
        put_message(client, uuid, msg)
        print(f'New record:\n\tuuid: {uuid}\n\ttext: {msg}')
        return 'Success'


if __name__ == '__main__':
    app_ = threading.Thread(target=start_app)
    hz = threading.Thread(target=start_hz)
    app_.start()
    hz.start()
