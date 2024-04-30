from flask import Flask
from hazelcast import HazelcastClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
args = parser.parse_args()

app = Flask(__name__)

messages = []


def message_added(event):
    last_message = event.item
    messages.append(last_message)
    print(f'Received message: {last_message}')
    msg_queue.remove(last_message)


@app.route('/', methods=['GET'])
def get_message():
    return ', '.join(messages)


if __name__ == '__main__':
    client = HazelcastClient()
    msg_queue = client.get_queue('messages')
    msg_queue.add_listener(include_value=True, item_added_func=message_added)
    app.run(debug=True, port=args.port)
    client.shutdown()
