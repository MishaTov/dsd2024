from flask import Flask
from hazelcast import HazelcastClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
args = parser.parse_args()

app = Flask(__name__)

messages = []


@app.route('/', methods=['GET'])
def get_message():
    if len(messages) < 5:
        client = HazelcastClient()
        msg_queue = client.get_queue('messages').blocking()
        last_message = msg_queue.poll()
        if last_message:
            messages.append(last_message)
            print(f'Received message: {last_message}')
    return ', '.join(messages)


if __name__ == '__main__':
    app.run(debug=True, port=args.port)
